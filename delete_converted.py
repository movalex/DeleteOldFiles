import logging
from pathlib import Path
from datetime import datetime, timedelta

FOLDERS = [
    "//Capture2/convert/processed",
    "//CAPTURE2/CONVERT_fast/processed",
    "//CAPTURE2/shared/MP4",
    "//Capture2/shared/NAEFIR/processed",
]

LOG_PATH = "//Capture2/shared/logs"


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
                total_size_purged += file_size
                # file.unlink()
                print(
                    f"Deleted {file.name} from {folder}, size: {file_size / (1024**2):.2f} MB"
                )
                # logger.info(f"Deleted {file.name} from {folder}, size: {file_size} bytes")
            except Exception as e:
                logger.error(f"Could not delete file {file.name}! Error message:\n{e}")

    formatted_total_size = format_size(total_size_purged)
    logger.info(f"Total number of files deleted: {count}")
    logger.info(f"Total size of files deleted: {formatted_total_size}")
    print(f"Total number of files deleted: {count}")
    print(f"Total size of files deleted: {formatted_total_size}")


def setup_logger(log_path):
    logger_folder = Path(log_path)
    logger_folder.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger("fileDeleter")
    logger.setLevel(logging.INFO)
    fh = logging.FileHandler(Path(logger_folder, "delete_converted.log"), "a", "utf-8")
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(message)s", "%Y-%m-%d %H:%M:%S"
    )
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    fh.close()
    return logger


if __name__ == "__main__":
    logger = setup_logger(LOG_PATH)
    for folder in FOLDERS:
        delete_files(folder)

    print("Done!")
