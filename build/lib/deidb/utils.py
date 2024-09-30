import json
from collections import defaultdict
import yaml
import importlib.resources
import logging
from deidb import type_functions
from pathlib import Path
import shutil

# Paths
IO_TEMPLATE_PATH = importlib.resources.files("deidb") / "templates" / "io.yaml"
# ENVS_PATH = importlib.resources.files("deidb") / "envs.txt"
# ENVS_PATH is in a file in root directory called .deidb
# make path from root
ENVS_PATH = Path.home() / ".deidb"


# Logging
def setup_logging(log_path):
    """Configures the logging system."""
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(log_path),
            logging.StreamHandler(),
        ],
    )


# File I/O
def load_yaml(filepath):
    """Loads a YAML file."""
    with open(filepath, "r") as file:
        return yaml.safe_load(file)


#


def save_json(filepath, data):
    """Saves a dictionary as a JSON file."""
    with open(filepath, "w") as file:
        json.dump(data, file)


# Key Dictionary


def make_key_dict(config, keydb_dir):
    """Creates a dictionary from the key files in the keydb directory."""
    key_dict = defaultdict(dict)
    for key_file in keydb_dir.iterdir():
        if key_file.stem in config["included"]:
            key_dict[key_file.stem] = json.load(key_file.open("r"))
    return key_dict


# Config Validation


def validate_config(config, file_cols):
    """Validates that the file columns match the config and functions are available."""
    config_cols = config["excluded"] + list(config["included"])
    missing_cols = [col for col in file_cols if col not in config_cols]
    if missing_cols:
        raise ValueError(f"Columns [{missing_cols}] are not in the config file.")

    missing_funcs = []
    for k, v in config["included"].items():
        func = v.get("function")
        if func is None or not hasattr(type_functions, func):
            missing_funcs.append(k)

    if missing_funcs:
        raise ValueError(
            f"Functions [{missing_funcs}] are not in the type_functions module."
        )


# Directory Management


def make_directory(directory_path):
    """Creates necessary directories and copies templates."""
    directory_path.mkdir(exist_ok=True)
    for sub_dir in ["keydb", "files", "logs", "config"]:
        (directory_path / sub_dir).mkdir(exist_ok=True)

    output_path = directory_path / "files" / "output.csv"
    if not output_path.exists():
        shutil.copy(IO_TEMPLATE_PATH, directory_path / "config" / "io.yaml")

    directories = get_activated_directories()
    if directory_path in directories:  # move to last
        directories.remove(directory_path)
    directories.append(directory_path)
    # now overwrite the envs.txt file
    with open(ENVS_PATH, "w") as file:
        file.write("Active directory: " + str(directory_path) + "\n")
        for directory in directories:
            file.write(str(directory) + "\n")


def get_activated_directories():
    if not ENVS_PATH.exists():
        return []

    with open(ENVS_PATH, "r") as file:
        return [Path(line.strip()) for line in file][1:]


def get_active_directory():
    """Retrieves the most recently activated directory."""
    directories = get_activated_directories()
    if not directories:
        raise FileNotFoundError(
            "No active directory found. Please run 'deidb activate <directory>' first."
        )
    return directories[-1]
