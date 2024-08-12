from pathlib import Path
from datetime import datetime, timedelta
import os
import logging

FOLDERS = [
    "//Capture2/convert/processed",
    "//CAPTURE2/CONVERT_fast/processed",
    "//CAPTURE2/shared/MP4",
    "//Capture2/shared/NAEFIR/processed",
]
# FOLDER = "."


def delete_files(folder, days=90):
    """
    get files modified more than `days` ago
    delete and log to file
    """
    folder = Path(folder)
    count = 0
    for file in folder.glob("*"):
        if not file.is_dir():
            file_modified = datetime.fromtimestamp(file.lstat().st_mtime)
            if datetime.now() - file_modified > timedelta(days):
                count += 1
                try:
                    file.unlink()
                    logger.info(f"deleted {file.name} from {folder}")
                except Exception as e:
                    logger.info(f"Could not delete file! Error message:\n{e}")


def setup_logger():
    logger_folder = Path(r"\\Capture2\shared\logs")
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
    logger = setup_logger()
    for folder in FOLDERS:
        delete_files(folder)

    print("Done!")
