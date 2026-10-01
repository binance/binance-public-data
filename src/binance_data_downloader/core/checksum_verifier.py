"""
Checksum Verifier

This module provides SHA256 checksum verification for downloaded files.
Supports cross-platform verification (Linux, macOS, Windows).
"""

import hashlib
import logging
import os
import platform
import subprocess
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


class ChecksumVerifier:
    """
    Verifies SHA256 checksums of downloaded files.

    Uses platform-appropriate tools:
    - Linux: sha256sum
    - macOS: shasum -a 256
    - Windows: Python hashlib (fallback for all platforms)
    """

    def __init__(self, use_platform_tool: bool = True):
        """
        Initialize the checksum verifier.

        Args:
            use_platform_tool: Whether to use platform-specific tools (sha256sum/shasum)
                              or fall back to pure Python implementation
        """
        self.use_platform_tool = use_platform_tool
        self.platform = platform.system()
        self._verify_platform_tool()

    def _verify_platform_tool(self) -> bool:
        """Check if platform-specific checksum tool is available."""
        if not self.use_platform_tool:
            return False

        tool_name = self._get_platform_tool_name()
        if not tool_name:
            return False

        try:
            subprocess.run(
                [tool_name, "--version"],
                capture_output=True,
                check=True,
                timeout=5
            )
            return True
        except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
            logger.debug(f"Platform checksum tool '{tool_name}' not available, using Python hashlib")
            return False

    def _get_platform_tool_name(self) -> Optional[str]:
        """Get the platform-specific checksum tool name."""
        if self.platform == "Linux":
            return "sha256sum"
        elif self.platform == "Darwin":  # macOS
            return "shasum"
        return None

    def calculate_checksum(self, file_path: str) -> Optional[str]:
        """
        Calculate SHA256 checksum of a file.

        Args:
            file_path: Path to the file

        Returns:
            Hexadecimal checksum string, or None if calculation fails
        """
        if not os.path.exists(file_path):
            logger.error(f"File not found for checksum calculation: {file_path}")
            return None

        # Try platform-specific tool first
        if self.use_platform_tool and self.platform in ("Linux", "Darwin"):
            checksum = self._calculate_with_platform_tool(file_path)
            if checksum:
                return checksum

        # Fall back to Python implementation
        return self._calculate_with_hashlib(file_path)

    def _calculate_with_platform_tool(self, file_path: str) -> Optional[str]:
        """Calculate checksum using platform-specific tool."""
        tool_name = self._get_platform_tool_name()
        if not tool_name:
            return None

        try:
            cmd = [tool_name]
            if self.platform == "Darwin":
                cmd.extend(["-a", "256"])
            cmd.append(file_path)

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True,
                timeout=300  # 5 minute timeout for large files
            )

            # Output format: "checksum  filename"
            output = result.stdout.strip()
            checksum = output.split()[0]
            return checksum
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
            logger.warning(f"Platform checksum tool failed: {e}")
            return None

    def _calculate_with_hashlib(self, file_path: str) -> Optional[str]:
        """Calculate checksum using Python hashlib."""
        try:
            sha256_hash = hashlib.sha256()
            with open(file_path, "rb") as f:
                # Read in chunks to handle large files
                for byte_block in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(byte_block)
            return sha256_hash.hexdigest()
        except Exception as e:
            logger.error(f"Failed to calculate checksum with hashlib: {e}")
            return None

    def verify_checksum(self, file_path: str, checksum_file_path: str) -> bool:
        """
        Verify a file's checksum against its CHECKSUM file.

        Args:
            file_path: Path to the data file
            checksum_file_path: Path to the .CHECKSUM file

        Returns:
            True if checksum matches, False otherwise
        """
        if not os.path.exists(checksum_file_path):
            logger.error(f"Checksum file not found: {checksum_file_path}")
            return False

        # Read expected checksum from .CHECKSUM file
        try:
            with open(checksum_file_path, 'r') as f:
                checksum_content = f.read().strip()
                # Format: "checksum  filename"
                expected_checksum = checksum_content.split()[0]
        except Exception as e:
            logger.error(f"Failed to read checksum file: {e}")
            return False

        # Calculate actual checksum
        actual_checksum = self.calculate_checksum(file_path)
        if actual_checksum is None:
            return False

        # Compare checksums
        if actual_checksum.lower() == expected_checksum.lower():
            logger.info(f"Checksum verified: {file_path}")
            return True
        else:
            logger.error(
                f"Checksum mismatch for {file_path}\n"
                f"Expected: {expected_checksum}\n"
                f"Actual: {actual_checksum}"
            )
            return False

    def download_and_verify_checksum(
        self,
        file_path: str,
        checksum_file_path: str
    ) -> tuple[bool, Optional[str]]:
        """
        Download checksum file and verify data file.

        Args:
            file_path: Path to the data file
            checksum_file_path: Path where checksum file should be

        Returns:
            Tuple of (success: bool, message: str)
        """
        if not os.path.exists(file_path):
            return False, f"Data file not found: {file_path}"

        if not os.path.exists(checksum_file_path):
            return False, f"Checksum file not found: {checksum_file_path}"

        is_valid = self.verify_checksum(file_path, checksum_file_path)
        if is_valid:
            return True, "Checksum verification passed"
        else:
            return False, "Checksum verification failed"


# Default checksum verifier instance
default_verifier = ChecksumVerifier()
