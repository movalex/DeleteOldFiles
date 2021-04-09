from pathlib import Path
from datetime import datetime, timedelta
import os
import logging

FOLDERS = ["//Capture2/convert/processed", "//CAPTURE2/CONVERT_fast/processed"]
# FOLDER = "."


def delete_files(folder, days=50):
    """
    get files modified more that `days` ago
    delete them and log to file
    """
    parent_folder = str(folder.parent).strip(os.sep)
    base_folder = os.path.basename(parent_folder)
    count = 0
    for file in folder.glob("*"):
        if not file.is_dir():
            file_modified = datetime.fromtimestamp(file.lstat().st_mtime)
            file_date = file_modified.strftime("%H:%M %d-%b-%Y")
            if datetime.now() - file_modified > timedelta(days):
                count += 1
                file.unlink()
                logger.info(
                    f"deleted {file.name} created at {file_date} in {base_folder}"
                )
    fh.close()


if __name__ == "__main__":
    # setup logger
    logger_folder = Path(FOLDERS[0]) / "log"
    logger_folder.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger("fileDeleter")
    logger.setLevel(logging.INFO)
    fh = logging.FileHandler(Path(logger_folder, "logfile.log"), "a", "utf-8")
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(message)s", "%Y-%m-%d %H:%M:%S"
    )
    fh.setFormatter(formatter)
    logger.addHandler(fh)

    for folder in FOLDERS:
        folder = Path(folder)
        delete_files(folder)

    print("Done!")
