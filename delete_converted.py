import logging
from pathlib import Path
from datetime import datetime, timedelta

FOLDERS = [
    "//Capture2/convert/processed",
    "//CAPTURE2/CONVERT_fast/processed",
    "//CAPTURE2/shared/MP4",
    "//Capture2/shared/NAEFIR/processed",
]

LOG_FILE = "//Capture2/shared/logs/delete_converted.log"


def setup_logger(name, log_file, level=logging.ERROR):
    """
    Function to set up a logger with the given name, log file, and logging level.
    """
    logger = logging.getLogger(name)
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(formatter)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)

    logger.setLevel(level)
    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)

    return logger


def format_size(size_bytes):
    """
    Returns the size in MB if less than 1 GB, otherwise in GB.
    """
    if size_bytes < 1024**3:  # Less than 1 GB
        size_mb = size_bytes / (1024 * 1024)
        return f"{size_mb:.2f} MB"
    else:  # 1 GB or more
        size_gb = size_bytes / (1024 * 1024 * 1024)
        return f"{size_gb:.2f} GB"


def delete_files(folder, days=90):
    """
    Get files modified more than `days` ago,
    delete and log to file.
    """
    folder = Path(folder)
    count = 0
    total_size_purged = 0

    if not folder.is_dir():
        logger.error(f"The folder {folder} does not exist or is not a directory.")
        return

    for file in folder.glob("*"):
        if file.is_dir():
            continue
        file_modified = datetime.fromtimestamp(file.lstat().st_mtime)
        if datetime.now() - file_modified > timedelta(days=days):
            count += 1
            try:
                file_size = file.stat().st_size
                file_size_formatted = format_size(file_size)
                total_size_purged += file_size
                # file.unlink()
                print(f"Deleted {file.name} from {folder}, {file_size_formatted}")
                logger.info(f"Deleted {file.name} from {folder}, {file_size} bytes")
            except Exception as e:
                logger.error(f"Could not delete file {file.name}! Error message:\n{e}")

    if count == 0:
        logger.debug("No files to delete")
        return

    formatted_total_size = format_size(total_size_purged)
    logger.info(f"Total number of files deleted in {folder.name}: {count}")
    logger.info(f"Total size of files deleted in {folder.name}: {formatted_total_size}")


if __name__ == "__main__":
    logger = setup_logger("fileDeleter", LOG_FILE)
    for folder in FOLDERS:
        delete_files(folder)

    print("Done!")
