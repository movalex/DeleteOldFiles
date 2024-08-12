import logging
import psutil
from pathlib import Path
from datetime import datetime, timedelta

FOLDERS = [
    "//Capture2/convert/processed",
    "//CAPTURE2/CONVERT_fast/processed",
    "//CAPTURE2/shared/MP4",
    # "//Capture2/shared/NAEFIR/processed",
]

LOG_FILE = "//Capture2/shared/logs/delete_converted.log"


def setup_logger(name, log_file, level=logging.DEBUG):
    """
    Function to set up a logger with the given name, log file, and logging level.
    """
    logger = logging.getLogger(name)
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
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


def is_file_opened(file_path):
    """
    Check if the file is currently opened by any process.
    """
    for proc in psutil.process_iter(["pid", "name"]):
        try:
            for item in proc.open_files():
                if item.path == file_path:
                    return True
        except (psutil.AccessDenied, psutil.NoSuchProcess):
            continue
    return False


def delete_files(folder, days=90):
    """
    Get files modified more than `days` ago,
    delete and log to file.
    """
    folder = Path(folder)
    count = 0
    total_size_purged = 0
    deleted_files = []
    errors = []

    if not folder.is_dir():
        error_message = f"The folder {folder} does not exist or is not a directory."
        return {"error": error_message}

    for file in folder.glob("*"):
        if file.is_dir():
            continue
        file_modified = datetime.fromtimestamp(file.lstat().st_mtime)
        if datetime.now() - file_modified > timedelta(days=days):
            # potentially slow, currently disabled
            # if is_file_opened(str(file)):
            #     logger.info(
            #         f"Skipping deletion of {file.name} as it is currently opened by another application."
            #     )
            #     continue
            try:
                file_size = file.stat().st_size
                total_size_purged += file_size
                file.unlink()  # delete files
                deleted_files.append((file.name, file_size))
                count += 1
            except Exception as e:
                error_message = (
                    f"Could not delete file {file.name}! Error message:\n{e}"
                )
                errors.append(error_message)

    return {
        "count": count,
        "folder_name": folder,
        "total_size_purged": total_size_purged,
        "deleted_files": deleted_files,
        "errors": errors,
    }


def log_deletion_summary(summary, logger):
    """
    Log the summary of the file deletion operation.
    """

    if "error" in summary:
        logger.error(f"Critical error encountered: {summary['error']}")
        return

    if not summary["count"]:
        return

    for file_name, file_size in summary["deleted_files"]:
        logger.debug(f"Deleted {file_name}, size: {format_size(file_size)}")

    current_folder = summary["folder_name"]
    logger.info(
        f"Total number of files deleted from {current_folder}: {summary['count']}"
    )

    if summary["errors"]:
        logger.error(f"Total files not deleted: {len(summary['errors'])}")
        if logger.getEffectiveLevel() == "INFO":
            logger.error("Use DEBUG level to list files not processed")
        for error in summary["errors"]:
            logger.debug(error)
    return summary["total_size_purged"]


if __name__ == "__main__":
    logger = setup_logger("fileDeleter", LOG_FILE)
    total_reclaimed_space = 0

    for folder in FOLDERS:
        summary = delete_files(folder)
        logger.info(f"Processing folder: {folder}")
        total_size = log_deletion_summary(summary, logger)
        if total_size:
            total_reclaimed_space += total_size
    if total_reclaimed_space:
        logger.info(f"Total reclaimed space: {format_size(total_reclaimed_space)}")

    print("Done!")
