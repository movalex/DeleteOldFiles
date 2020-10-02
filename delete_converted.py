from pathlib import Path
from datetime import datetime, timedelta
import os
import logging

FOLDERS = ["//Capture2/convert/processed", "//CAPTURE2/CONVERT_fast/processed"]
# FOLDER = "."

logger = logging.getLogger("fileDeleter")
logger.setLevel(logging.INFO)


def delete_files(filepath, days=50):
    """
    get files modified more that `days` ago
    delete them and log to file
    """

    folder_processed = Path(filepath)
    count = 0
    for file in folder_processed.glob("*"):
        if not file.is_dir():
            print(file)
            file_modified = datetime.fromtimestamp(file.lstat().st_mtime)
            file_date = file_modified.strftime("%H:%M %d-%b-%Y")
            if datetime.now() - file_modified > timedelta(days):
                count += 1
                # file.unlink()
                logger.info(f"deleted {file.name} created at {file_date}")
    if count == 0:
        logger.info("no old files found")
    fh.close()


if __name__ == "__main__":
    for folder in FOLDERS:
        folder = Path(folder)
        logger_folder = folder / "log"
        logger_folder.mkdir(parents=True, exist_ok=True)
        fh = logging.FileHandler(Path(folder, "log/logfile.log"), "a", "utf-8")
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(message)s", "%Y-%m-%d %H:%M:%S"
        )
        fh.setFormatter(formatter)
        logger.addHandler(fh)
        delete_files(folder)
