from pathlib import Path
from datetime import datetime, timedelta
import os
import logging

FOLDERS = [
    "//Capture2/convert/processed",
    "//CAPTURE2/CONVERT_fast/processed",
    "//CAPTURE2/Capture2/SHARED/MP4",
]
# FOLDER = "."


def delete_files(logger, folder, days=90):
    """
    get files modified more that `days` ago
    delete them and log to file
    """
    folder = Path(folder)
    parent_folder = str(folder.parent).strip(os.sep)
    base_folder = os.path.basename(parent_folder)
    count = 0
    for file in folder.glob("*"):
        if not file.is_dir():
            file_modified = datetime.fromtimestamp(file.lstat().st_mtime)
            file_date = file_modified.strftime("%H:%M %d-%b-%Y")
            if datetime.now() - file_modified > timedelta(days):
                count += 1
                try:
                    file.unlink()
                    logger.info(f"deleted {file.name} from {base_folder}")
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
        delete_files(logger, folder)

    print("Done!")
