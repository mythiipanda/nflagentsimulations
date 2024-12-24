import os
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("rename.log"),
        logging.StreamHandler()
    ]
)

def rename_files(base_dir: str):
    """
    Renames 'special-teams_2023.csv' to 'special_teams_2023.csv' in each team directory.

    Args:
        base_dir: The base directory containing all team directories.
    """
    logging.info(f"Starting renaming process in base directory: {base_dir}")
    for root, dirs, files in os.walk(base_dir):
        for file in files:
            if file == "special-teams_2023.csv":
                old_path = os.path.join(root, file)
                new_file = "special_teams_2023.csv"
                new_path = os.path.join(root, new_file)
                try:
                    os.rename(old_path, new_path)
                    logging.info(f"Renamed: {old_path} -> {new_path}")
                except Exception as e:
                    logging.error(f"Failed to rename {old_path} to {new_path}: {e}")

if __name__ == "__main__":
    BASE_DIRECTORY = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    rename_files(BASE_DIRECTORY)
    logging.info("Renaming process completed.")