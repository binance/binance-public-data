#!/usr/bin/env python3
"""
Binance Data Merge Script - Merge ZIP files to Single CSV (Memory Efficient)

This script extracts and merges all ZIP files from a folder into a single CSV file,
sorted by time in ascending order. Uses multi-threaded extraction and streaming
merge to handle large datasets efficiently.

Features:
- Multi-threaded ZIP extraction for faster processing
- Streaming merge to avoid memory overflow on large datasets
- Auto-detects symbol and interval from folder path
- Generates output filename: SYMBOL_INTERVAL_STARTDATE_ENDDATE.csv

Examples:
    # Merge klines data (specify folder containing ZIP files)
    python3 scripts/merge-zip-to-csv.py -folder data/futures/um/daily/klines/BTCUSDT/1m

    # Specify custom output directory
    python3 scripts/merge-zip-to-csv.py -folder data/futures/um/daily/klines/BTCUSDT/1m -output merged

    # Specify custom output filename
    python3 scripts/merge-zip-to-csv.py -folder data/futures/um/daily/klines/BTCUSDT/1m -o my_data.csv

    # Limit date range for output
    python3 scripts/merge-zip-to-csv.py -folder data/futures/um/daily/klines/BTCUSDT/1m -startDate 2023-01-01 -endDate 2023-12-31

    # Set number of threads for extraction
    python3 scripts/merge-zip-to-csv.py -folder data/futures/um/daily/klines/BTCUSDT/1m -workers 8
"""

import argparse
import csv
import logging
import os
import re
import sys
import tempfile
import zipfile
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path
from typing import List, Tuple, Optional


# Binance Klines columns (raw data has no headers)
# See: https://github.com/binance/binance-public-data/
KLINES_COLUMNS = [
    'Date',           # open_time (timestamp in milliseconds)
    'Open',           # open price
    'High',           # high price
    'Low',            # low price
    'Close',          # close price
    'Volume',         # volume
    'close_time',     # close time (timestamp in milliseconds)
    'quote_volume',   # quote asset volume
    'trades',         # number of trades
    'taker_buy_base', # taker buy base asset volume
    'taker_buy_quote',# taker buy quote asset volume
    'ignore'          # ignore
]


def setup_logger(level: str = 'INFO') -> logging.Logger:
    """Setup logger."""
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    return logging.getLogger(__name__)


def parse_symbol_interval_from_path(folder_path: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Parse symbol and interval from folder path.

    Args:
        folder_path: Path to the folder containing ZIP files

    Returns:
        Tuple of (symbol, interval) or (None, None) if not found
    """
    path_parts = Path(folder_path).parts

    symbol = None
    interval = None

    # Try to find symbol (e.g., BTCUSDT, ETHUSDT, etc.)
    for part in path_parts:
        # Symbol pattern: USDT/BUSD at end, all caps
        if re.match(r'^[A-Z]+USDT$', part) or re.match(r'^[A-Z]+BUSD$', part) or \
           re.match(r'^[A-Z]+USD_PERP$', part) or re.match(r'^[A-Z]+USDC$', part):
            symbol = part
            break

    # Try to find interval (e.g., 1m, 5m, 15m, 1h, 4h, 1d, etc.)
    interval_patterns = [
        r'^(\d+m)$',      # 1m, 5m, 15m
        r'^(\d+h)$',      # 1h, 4h, 12h
        r'^(\d+d)$',      # 1d, 3d
        r'^(1w|1M)$',     # 1w, 1M
    ]
    for part in path_parts:
        for pattern in interval_patterns:
            if re.match(pattern, part):
                interval = part
                break
        if interval:
            break

    return symbol, interval


def extract_single_zip(args: Tuple[str, str]) -> Tuple[str, Optional[str]]:
    """
    Extract a single ZIP file.

    Args:
        args: Tuple of (zip_path, temp_dir)

    Returns:
        Tuple of (csv_filename, error_message) - error_message is None if successful
    """
    zip_path, temp_dir = args
    zip_filename = os.path.basename(zip_path)

    try:
        with zipfile.ZipFile(zip_path, 'r') as zf:
            for file_info in zf.infolist():
                if file_info.filename.endswith('.csv'):
                    # Extract to temp directory
                    zf.extract(file_info, temp_dir)
                    return (file_info.filename, None)
        return (zip_filename, "No CSV file found in ZIP")
    except Exception as e:
        return (zip_filename, str(e))


def extract_zip_files_parallel(
    folder_path: str,
    temp_dir: str,
    max_workers: int,
    logger: logging.Logger
) -> List[str]:
    """
    Extract all ZIP files in parallel using multiple threads.

    Args:
        folder_path: Path to folder containing ZIP files
        temp_dir: Temporary directory for extracted files
        max_workers: Number of threads to use
        logger: Logger instance

    Returns:
        List of extracted CSV file paths (sorted)
    """
    zip_files = [
        os.path.join(folder_path, f)
        for f in os.listdir(folder_path)
        if f.endswith('.zip')
    ]

    if not zip_files:
        logger.warning(f"No ZIP files found in {folder_path}")
        return []

    logger.info(f"Found {len(zip_files)} ZIP files")
    logger.info(f"Extracting with {max_workers} threads...")

    # Prepare arguments for parallel processing
    extract_args = [(zip_path, temp_dir) for zip_path in zip_files]

    csv_files = []
    failed_files = []

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(extract_single_zip, args): args[0] for args in extract_args}

        for future in as_completed(futures):
            csv_filename, error = future.result()
            if error is None:
                csv_path = os.path.join(temp_dir, csv_filename)
                csv_files.append(csv_path)
            else:
                failed_files.append((csv_filename, error))
                logger.error(f"Failed to extract {csv_filename}: {error}")

    # Sort CSV files by filename (which contains date info)
    csv_files.sort()

    logger.info(f"Extracted {len(csv_files)} CSV files successfully")
    if failed_files:
        logger.warning(f"Failed to extract {len(failed_files)} files")

    return csv_files


def detect_time_column(csv_path: str) -> Optional[str]:
    """
    Detect the time column name by reading the first row of a CSV file.

    Args:
        csv_path: Path to CSV file

    Returns:
        Name of the time column or None
    """
    try:
        with open(csv_path, 'r', newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            headers = next(reader, None)
            if headers:
                # Common time column names in Binance data
                time_columns = [
                    'open_time', 'openTime', 'timestamp',
                    'time', 'date', 'datetime',
                    'trade_time', 'close_time'
                ]
                for col in time_columns:
                    if col in headers:
                        return col
                # Default to first column
                return headers[0] if headers else None
    except Exception:
        pass
    return None


def convert_klines_row(row: List[str]) -> List[str]:
    """
    Convert klines row: transform timestamp to datetime string for compatibility.

    Args:
        row: Raw klines data row

    Returns:
        Row with first column (Date) converted to datetime string
    """
    if row and len(row) > 0:
        try:
            ts = int(row[0])
            dt = datetime.fromtimestamp(ts / 1000)
            # Format: YYYY-MM-DD HH:MM:SS
            row = row.copy()
            row[0] = dt.strftime('%Y-%m-%d %H:%M:%S')
        except (ValueError, TypeError):
            pass
    return row


def is_binance_klines_data(csv_path: str) -> bool:
    """
    Check if CSV file is Binance klines data (no headers, 12 columns, first column is timestamp).

    Args:
        csv_path: Path to CSV file

    Returns:
        True if file appears to be Binance klines data without headers
    """
    try:
        with open(csv_path, 'r', newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            first_row = next(reader, None)
            if first_row and len(first_row) >= 6:
                # Check if first column looks like a timestamp (13-digit milliseconds)
                try:
                    ts = int(first_row[0])
                    # Valid timestamp range: 2017-01-01 to 2030-01-01 in milliseconds
                    if 1483228800000 <= ts <= 1893456000000:
                        # Check if other columns are numeric (prices/volumes)
                        float(first_row[1])  # open
                        float(first_row[2])  # high
                        float(first_row[3])  # low
                        float(first_row[4])  # close
                        float(first_row[5])  # volume
                        return True
                except (ValueError, IndexError):
                    pass
    except Exception:
        pass
    return False


def read_csv_batches(
    csv_files: List[str],
    batch_size: int = 50,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    logger: logging.Logger = None,
    is_klines: bool = False
):
    """
    Generator that yields batches of rows from CSV files.

    Args:
        csv_files: List of CSV file paths (sorted by filename)
        batch_size: Number of CSV files to process per batch
        start_date: Optional start date filter (YYYY-MM-DD)
        end_date: Optional end date filter (YYYY-MM-DD)
        logger: Logger instance
        is_klines: If True, treat files as headerless Binance klines data

    Yields:
        Tuples of (headers, rows_batch, total_rows_in_batch)
    """
    # Convert date filters to timestamps if provided
    start_ts = None
    end_ts = None
    if start_date:
        start_dt = datetime.strptime(start_date, '%Y-%m-%d')
        start_ts = int(start_dt.timestamp() * 1000)
    if end_date:
        end_dt = datetime.strptime(end_date, '%Y-%m-%d')
        # Include the entire end date
        from datetime import timedelta
        end_dt = end_dt + timedelta(days=1)
        end_ts = int(end_dt.timestamp() * 1000)

    headers = None
    time_col_idx = 0
    total_rows = 0

    # For klines data, use predefined headers
    if is_klines:
        headers = KLINES_COLUMNS
        time_col_idx = 0  # Date column is first

    for i in range(0, len(csv_files), batch_size):
        batch = csv_files[i:i + batch_size]
        batch_rows = []
        batch_count = 0

        if logger:
            logger.debug(f"Processing batch {i // batch_size + 1}/{(len(csv_files) + batch_size - 1) // batch_size}")

        for csv_file in batch:
            try:
                with open(csv_file, 'r', newline='', encoding='utf-8') as f:
                    reader = csv.reader(f)

                    if is_klines:
                        # Klines data has no headers, read all rows as data
                        for row in reader:
                            if len(row) <= time_col_idx:
                                continue

                            # Apply date filters if specified
                            if start_ts or end_ts:
                                try:
                                    row_ts = int(row[time_col_idx])
                                    if start_ts and row_ts < start_ts:
                                        continue
                                    if end_ts and row_ts >= end_ts:
                                        continue
                                except (ValueError, IndexError):
                                    pass

                            batch_rows.append(row)
                            batch_count += 1
                            total_rows += 1
                    else:
                        # Regular CSV with headers
                        file_headers = next(reader, None)

                        if file_headers:
                            if headers is None:
                                headers = file_headers
                                # Find time column index
                                time_col_name = detect_time_column(csv_file)
                                if time_col_name and time_col_name in file_headers:
                                    time_col_idx = file_headers.index(time_col_name)

                            # Read rows
                            for row in reader:
                                if len(row) <= time_col_idx:
                                    continue

                                # Apply date filters if specified
                                if start_ts or end_ts:
                                    try:
                                        row_ts = int(row[time_col_idx])
                                        if start_ts and row_ts < start_ts:
                                            continue
                                        if end_ts and row_ts >= end_ts:
                                            continue
                                    except (ValueError, IndexError):
                                        pass

                                batch_rows.append(row)
                                batch_count += 1
                                total_rows += 1

            except Exception as e:
                if logger:
                    logger.error(f"Error reading {csv_file}: {e}")

        # Sort this batch by time column
        if batch_rows and headers:
            try:
                batch_rows.sort(key=lambda x: int(x[time_col_idx]) if len(x) > time_col_idx else 0)
            except (ValueError, IndexError):
                pass  # Keep original order if sorting fails

        yield headers, batch_rows, batch_count


def merge_sorted_batches(
    csv_files: List[str],
    output_path: str,
    batch_size: int = 50,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    logger: logging.Logger = None,
    is_klines: bool = False,
    convert_datetime: bool = True
) -> Tuple[int, str, str]:
    """
    Merge CSV files using external merge sort algorithm.

    Reads files in batches, sorts each batch, and writes to output.
    Uses a final in-memory sort of batch checkpoints for complete ordering.

    Args:
        csv_files: List of CSV file paths (sorted by filename)
        output_path: Path to output CSV file
        batch_size: Number of CSV files to process per batch
        start_date: Optional start date filter (YYYY-MM-DD)
        end_date: Optional end date filter (YYYY-MM-DD)
        logger: Logger instance
        is_klines: If True, treat files as headerless Binance klines data
        convert_datetime: If True and is_klines, convert timestamp to datetime string

    Returns:
        Tuple of (total_rows, first_timestamp, last_timestamp)
    """
    if logger:
        logger.info("Starting streaming merge...")
        if is_klines:
            logger.info("Detected Binance klines data (headerless), adding column names...")

    # Since Binance files are named with dates (e.g., BTCUSDT-1m-2020-01-01.csv),
    # and we sorted by filename, the data is approximately in order.
    # We'll process in batches and do a final pass.

    temp_sorted_files = []
    headers = None
    total_rows = 0
    first_ts = None
    last_ts = None

    with tempfile.TemporaryDirectory() as temp_dir:
        # First pass: Read, filter, and sort batches
        for batch_headers, batch_rows, batch_count in read_csv_batches(
            csv_files, batch_size, start_date, end_date, logger, is_klines=is_klines
        ):
            if headers is None and batch_headers:
                headers = batch_headers

            if batch_rows:
                total_rows += batch_count

                # Track first and last timestamps
                if batch_rows:
                    try:
                        if first_ts is None:
                            first_ts = batch_rows[0][0]
                        last_ts = batch_rows[-1][0]
                    except IndexError:
                        pass

                # Write sorted batch to temp file
                temp_file = os.path.join(temp_dir, f"batch_{len(temp_sorted_files)}.csv")
                with open(temp_file, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerows(batch_rows)
                temp_sorted_files.append(temp_file)

                if logger:
                    logger.debug(f"Wrote batch {len(temp_sorted_files)}: {batch_count} rows")

        # Second pass: Merge all sorted batches using k-way merge
        if logger:
            logger.info(f"Merging {len(temp_sorted_files)} sorted batches...")

        with open(output_path, 'w', newline='', encoding='utf-8') as out_file:
            writer = csv.writer(out_file)

            # Write headers
            if headers:
                writer.writerow(headers)

            # Use priority queue for k-way merge
            import heapq

            # Open all temp files and read first row from each
            file_handles = []
            heap = []

            for i, temp_file in enumerate(temp_sorted_files):
                f = open(temp_file, 'r', newline='', encoding='utf-8')
                reader = csv.reader(f)
                try:
                    first_row = next(reader)
                    heapq.heappush(heap, (first_row[0], i, first_row))
                    file_handles.append((f, reader))
                except StopIteration:
                    f.close()

            # K-way merge
            merge_count = 0
            while heap:
                time_key, file_idx, row = heapq.heappop(heap)
                # Convert timestamp to datetime string for klines data
                if is_klines and convert_datetime:
                    row = convert_klines_row(row)
                writer.writerow(row)
                merge_count += 1

                # Progress indicator
                if merge_count % 100000 == 0 and logger:
                    logger.debug(f"Merged {merge_count} rows...")

                # Get next row from this file
                f, reader = file_handles[file_idx]
                try:
                    next_row = next(reader)
                    heapq.heappush(heap, (next_row[0], file_idx, next_row))
                except StopIteration:
                    f.close()

            # Close any remaining files
            for f, reader in file_handles:
                if not f.closed:
                    f.close()

    return total_rows, first_ts or '', last_ts or ''


def generate_output_filename(
    symbol: Optional[str],
    interval: Optional[str],
    first_ts: str,
    last_ts: str,
    output_dir: str,
    custom_name: Optional[str] = None
) -> str:
    """
    Generate output filename in format: SYMBOL_INTERVAL_STARTDATE_ENDDATE.csv

    Args:
        symbol: Trading symbol
        interval: Time interval
        first_ts: First timestamp (milliseconds)
        last_ts: Last timestamp (milliseconds)
        output_dir: Output directory
        custom_name: Custom filename (overrides auto-generated)

    Returns:
        Full path to output file
    """
    if custom_name:
        if not custom_name.endswith('.csv'):
            custom_name += '.csv'
        return os.path.join(output_dir, custom_name)

    # Convert timestamps to dates
    try:
        if first_ts and last_ts:
            first_dt = datetime.fromtimestamp(int(first_ts) / 1000)
            last_dt = datetime.fromtimestamp(int(last_ts) / 1000)
            start_date = first_dt.strftime('%Y%m%d')
            end_date = last_dt.strftime('%Y%m%d')
        else:
            start_date = 'unknown'
            end_date = 'unknown'
    except (ValueError, TypeError):
        start_date = 'unknown'
        end_date = 'unknown'

    # Build filename
    parts = []
    if symbol:
        parts.append(symbol)
    if interval:
        parts.append(interval)
    parts.append(start_date)
    parts.append(end_date)

    filename = '_'.join(parts) + '.csv'
    return os.path.join(output_dir, filename)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Binance Data Merge Script - Memory Efficient Streaming Merge',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )

    parser.add_argument(
        '-folder',
        type=str,
        required=True,
        help='Folder containing ZIP files to merge (e.g., data/futures/um/daily/klines/BTCUSDT/1m)'
    )

    parser.add_argument(
        '-output', '-o',
        type=str,
        default='.',
        help='Output directory for merged CSV file (default: current directory)'
    )

    parser.add_argument(
        '-filename',
        type=str,
        default=None,
        help='Custom output filename (default: auto-generated as SYMBOL_INTERVAL_STARTDATE_ENDDATE.csv)'
    )

    parser.add_argument(
        '-startDate',
        type=str,
        default=None,
        help='Filter data from this date (YYYY-MM-DD format)'
    )

    parser.add_argument(
        '-endDate',
        type=str,
        default=None,
        help='Filter data until this date (YYYY-MM-DD format)'
    )

    parser.add_argument(
        '-s', '--symbol',
        type=str,
        default=None,
        help='Trading symbol (auto-detected from folder path if not specified)'
    )

    parser.add_argument(
        '-i', '--interval',
        type=str,
        default=None,
        help='Time interval (auto-detected from folder path if not specified)'
    )

    parser.add_argument(
        '-workers', '-w',
        type=int,
        default=8,
        help='Number of threads for ZIP extraction (default: 8)'
    )

    parser.add_argument(
        '-batch-size',
        type=int,
        default=100,
        help='Number of files to process per batch (default: 100). Lower uses less memory, higher is faster.'
    )

    parser.add_argument(
        '-log-level',
        type=str,
        default='INFO',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
        help='Logging level (default: INFO)'
    )

    args = parser.parse_args()

    # Setup logging
    logger = setup_logger(args.log_level)

    # Validate folder path
    folder_path = args.folder
    if not os.path.isdir(folder_path):
        logger.error(f"Folder not found: {folder_path}")
        return 1

    # Parse symbol and interval from folder path
    symbol, interval = parse_symbol_interval_from_path(folder_path)

    # Override with command-line args if provided
    if args.symbol:
        symbol = args.symbol
    if args.interval:
        interval = args.interval

    logger.info("=" * 70)
    logger.info("Binance Data Merge Script (Memory Efficient)")
    logger.info("=" * 70)
    logger.info(f"Input folder: {folder_path}")
    if symbol:
        logger.info(f"Symbol: {symbol}")
    if interval:
        logger.info(f"Interval: {interval}")
    logger.info(f"Extraction threads: {args.workers}")
    logger.info(f"Batch size: {args.batch_size} files")

    # Create output directory
    output_dir = args.output
    os.makedirs(output_dir, exist_ok=True)
    logger.info(f"Output directory: {output_dir}")

    # Create temp directory for extraction
    start_time = datetime.now()
    logger.info(f"Started at: {start_time}")

    with tempfile.TemporaryDirectory() as temp_dir:
        logger.info(f"Temporary directory: {temp_dir}")

        # Extract ZIP files in parallel
        extract_start = datetime.now()
        csv_files = extract_zip_files_parallel(
            folder_path, temp_dir, args.workers, logger
        )

        if not csv_files:
            logger.error("No CSV files extracted. Exiting.")
            return 1

        extract_time = (datetime.now() - extract_start).total_seconds()
        logger.info(f"Extraction completed in {extract_time:.1f} seconds")

        # Merge CSV files using streaming approach
        merge_start = datetime.now()

        # Generate output path (temporary until we know date range)
        output_path = os.path.join(output_dir, args.filename if args.filename else 'temp_output.csv')

        # Detect if source data is headerless Binance klines
        is_klines = False
        if csv_files:
            is_klines = is_binance_klines_data(csv_files[0])
            if is_klines:
                logger.info("Detected Binance klines data format (headerless)")
                logger.info(f"Will add columns: {', '.join(KLINES_COLUMNS[:6])}")

        total_rows, first_ts, last_ts = merge_sorted_batches(
            csv_files,
            output_path,
            batch_size=args.batch_size,
            start_date=args.startDate,
            end_date=args.endDate,
            logger=logger,
            is_klines=is_klines
        )

        merge_time = (datetime.now() - merge_start).total_seconds()
        logger.info(f"Merge completed in {merge_time:.1f} seconds")

        # Rename output file with proper name if not custom
        if not args.filename:
            final_output_path = generate_output_filename(
                symbol=symbol,
                interval=interval,
                first_ts=first_ts,
                last_ts=last_ts,
                output_dir=output_dir
            )
            # Rename temp file to final name
            if os.path.exists(final_output_path):
                os.remove(final_output_path)
            os.rename(output_path, final_output_path)
            output_path = final_output_path

        logger.info(f"Output file: {output_path}")
        logger.info(f"Total records: {total_rows:,}")

        # Print date range info
        if first_ts and last_ts:
            try:
                first_dt = datetime.fromtimestamp(int(first_ts) / 1000)
                last_dt = datetime.fromtimestamp(int(last_ts) / 1000)
                logger.info(f"Date range: {first_dt} to {last_dt}")
            except (ValueError, TypeError):
                pass

    total_time = (datetime.now() - start_time).total_seconds()
    logger.info("=" * 70)
    logger.info(f"Merge completed successfully in {total_time:.1f} seconds!")
    logger.info("=" * 70)

    return 0


if __name__ == "__main__":
    sys.exit(main())
