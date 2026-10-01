"""
Progress Tracker

This module provides download progress tracking and statistics.
"""

import logging
import sys
import time
from dataclasses import dataclass, field
from typing import Optional

logger = logging.getLogger(__name__)


@dataclass
class DownloadStats:
    """Statistics for download operations."""
    total_files: int = 0
    successful_downloads: int = 0
    failed_downloads: int = 0
    skipped_files: int = 0
    start_time: float = field(default_factory=time.time)
    end_time: Optional[float] = None
    total_bytes: int = 0

    @property
    def duration(self) -> float:
        """Get the total duration in seconds."""
        if self.end_time:
            return self.end_time - self.start_time
        return time.time() - self.start_time

    @property
    def success_rate(self) -> float:
        """Get the success rate as a percentage."""
        if self.total_files == 0:
            return 0.0
        return (self.successful_downloads / self.total_files) * 100

    def add_success(self, bytes_downloaded: int = 0):
        """Record a successful download."""
        self.successful_downloads += 1
        self.total_bytes += bytes_downloaded

    def add_failure(self):
        """Record a failed download."""
        self.failed_downloads += 1

    def add_skip(self):
        """Record a skipped file (already exists)."""
        self.skipped_files += 1

    def finish(self):
        """Mark the download session as finished."""
        self.end_time = time.time()


class ProgressTracker:
    """
    Tracks and displays download progress.

    Provides both console progress bars and detailed statistics.
    """

    def __init__(
        self,
        total_items: int,
        show_bar: bool = True,
        show_statistics: bool = True,
        update_interval: int = 5
    ):
        """
        Initialize the progress tracker.

        Args:
            total_items: Total number of items to process
            show_bar: Whether to show progress bar
            show_statistics: Whether to show detailed statistics
            update_interval: Update interval for statistics (in items)
        """
        self.total_items = total_items
        self.current_item = 0
        self.show_bar = show_bar
        self.show_statistics = show_statistics
        self.update_interval = update_interval
        self.stats = DownloadStats(total_files=total_items)
        self.last_update = 0

    def update(self, symbol: str, success: bool, skipped: bool = False):
        """
        Update progress after processing an item.

        Args:
            symbol: Symbol being processed
            success: Whether the operation succeeded
            skipped: Whether the file was skipped (already exists)
        """
        self.current_item += 1

        if skipped:
            self.stats.add_skip()
        elif success:
            self.stats.add_success()
        else:
            self.stats.add_failure()

        # Show progress bar
        if self.show_bar:
            self._show_progress_bar(symbol)

        # Show periodic statistics
        if self.show_statistics and self.current_item - self.last_update >= self.update_interval:
            self._show_statistics()
            self.last_update = self.current_item

    def _show_progress_bar(self, symbol: str):
        """Show console progress bar."""
        percentage = (self.current_item / self.total_items) * 100
        bar_length = 50
        # Cap filled at bar_length to prevent overflow
        filled = min(int(bar_length * self.current_item / self.total_items), bar_length)
        bar = '#' * filled + '.' * (bar_length - filled)

        print(
            f"\r[{bar}] {self.current_item}/{self.total_items} "
            f"({percentage:.1f}%) - {symbol}",
            end='',
            flush=True
        )

        # New line when complete
        if self.current_item >= self.total_items:
            print()

    def _show_statistics(self):
        """Show current download statistics."""
        logger.info(
            f"Progress: {self.current_item}/{self.total_items} | "
            f"Success: {self.stats.successful_downloads} | "
            f"Failed: {self.stats.failed_downloads} | "
            f"Skipped: {self.stats.skipped_files}"
        )

    def finish(self, show_summary: bool = True):
        """
        Mark progress as complete and show final statistics.

        Args:
            show_summary: Whether to show final summary
        """
        self.stats.finish()

        if self.show_statistics and show_summary:
            self._show_final_summary()

    def _show_final_summary(self):
        """Show final download summary."""
        print("\n" + "=" * 60)
        print("Download Summary")
        print("=" * 60)
        print(f"Total files:        {self.stats.total_files}")
        print(f"Successful:         {self.stats.successful_downloads}")
        print(f"Failed:             {self.stats.failed_downloads}")
        print(f"Skipped:            {self.stats.skipped_files}")
        print(f"Success rate:       {self.stats.success_rate:.1f}%")
        print(f"Duration:           {self.stats.duration:.2f} seconds")
        if self.stats.total_bytes > 0:
            mb_downloaded = self.stats.total_bytes / (1024 * 1024)
            print(f"Data downloaded:    {mb_downloaded:.2f} MB")
        print("=" * 60)


class MultiProgressTracker:
    """
    Tracks progress across multiple download sessions.

    Useful for aggregating statistics when downloading multiple data types.
    """

    def __init__(self, show_summary: bool = True):
        """
        Initialize the multi-session tracker.

        Args:
            show_summary: Whether to show summary after each session
        """
        self.sessions: list[DownloadStats] = []
        self.show_summary = show_summary

    def new_session(self, total_items: int) -> ProgressTracker:
        """
        Start a new tracking session.

        Args:
            total_items: Total items in this session

        Returns:
            ProgressTracker for the new session
        """
        tracker = ProgressTracker(
            total_items=total_items,
            show_statistics=self.show_summary
        )
        return tracker

    def add_session_stats(self, stats: DownloadStats):
        """Add completed session statistics."""
        self.sessions.append(stats)

    def show_aggregate_summary(self):
        """Show aggregated statistics across all sessions."""
        if not self.sessions:
            return

        total = DownloadStats()
        for session in self.sessions:
            total.total_files += session.total_files
            total.successful_downloads += session.successful_downloads
            total.failed_downloads += session.failed_downloads
            total.skipped_files += session.skipped_files
            total.total_bytes += session.total_bytes

        # Use earliest start and latest end
        if self.sessions:
            total.start_time = min(s.start_time for s in self.sessions)
            end_times = [s.end_time for s in self.sessions if s.end_time]
            if end_times:
                total.end_time = max(end_times)

        print("\n" + "=" * 60)
        print("Aggregate Download Summary")
        print("=" * 60)
        print(f"Sessions:           {len(self.sessions)}")
        print(f"Total files:        {total.total_files}")
        print(f"Successful:         {total.successful_downloads}")
        print(f"Failed:             {total.failed_downloads}")
        print(f"Skipped:            {total.skipped_files}")
        print(f"Success rate:       {total.success_rate:.1f}%")
        print(f"Duration:           {total.duration:.2f} seconds")
        if total.total_bytes > 0:
            mb_downloaded = total.total_bytes / (1024 * 1024)
            print(f"Data downloaded:    {mb_downloaded:.2f} MB")
        print("=" * 60)
