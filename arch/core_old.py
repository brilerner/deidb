from datetime import datetime
import json
import pandas as pd
from collections import defaultdict
import shutil
from pathlib import Path
import yaml
import logging
import importlib.resources

from deidb import type_functions

# Paths
IO_TEMPLATE_PATH = importlib.resources.files("deidb") / "templates" / "io.yaml"
ENVS_PATH = importlib.resources.files("deidb") / "envs.txt"

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

def load_yaml(filepath):
    """Loads a YAML file."""
    with open(filepath, "r") as file:
        return yaml.safe_load(file)

def save_json(filepath, data):
    """Saves a dictionary as a JSON file."""
    with open(filepath, "w") as file:
        json.dump(data, file)

def make_key_dict(config, keydb_dir):
    """Creates a dictionary from the key files in the keydb directory."""
    key_dict = defaultdict(dict)
    for key_file in keydb_dir.iterdir():
        if key_file.stem in config["included"]:
            key_dict[key_file.stem] = json.load(key_file.open("r"))
    return key_dict

def make_directory(directory_path):
    """Creates necessary directories and copies templates."""
    directory_path.mkdir(exist_ok=True)
    for sub_dir in ["keydb", "files", "logs", "config"]:
        (directory_path / sub_dir).mkdir(exist_ok=True)
    
    shutil.copy(IO_TEMPLATE_PATH, directory_path / "config" / "io.yaml")

    mode = "a" if ENVS_PATH.exists() else "w"
    with open(ENVS_PATH, mode) as file:
        file.write(f"{directory_path.name}\n")

def init_directory(directory_name):
    """Initializes a new directory for the project."""
    if ENVS_PATH.exists():
        with open(ENVS_PATH, "r") as file:
            if directory_name in file.read():
                print(f"Directory {directory_name} already exists.")
                exit(1)
    
    make_directory(Path.cwd() / directory_name)

def get_active_dir():
    """Retrieves the most recently activated directory."""
    if not ENVS_PATH.exists():
        print("No active directory found. Please run 'deidb init <directory_name>' first.")
        exit(1)
    with open(ENVS_PATH, "r") as file:
        return Path(file.readlines()[-1].strip())

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
        raise ValueError(f"Functions [{missing_funcs}] are not in the type_functions module.")

def deidentify_file(filepath, active_dir):
    """Deidentifies a file according to the config and keydb."""
    config_dir = active_dir / "config"
    io_path = config_dir / "io.yaml"
    keydb_dir = active_dir / "keydb"
    logs_dir = active_dir / "logs"
    log_path = logs_dir / "deidentify_file.log"

    setup_logging(log_path)
    
    file_df = pd.read_csv(filepath)
    config = load_yaml(io_path)
    validate_config(config, file_df.columns)
    
    key_dict = make_key_dict(config, keydb_dir)
    
    for col in file_df.columns:
        if col not in config["included"]:
            continue
        
        type_func_str = config["type_functions"][config["included"][col]["type"]]
        type_func = getattr(type_functions, type_func_str)
        
        for i, val in enumerate(file_df[col]):
            if val in key_dict[col]:
                file_df.loc[i, col] = key_dict[col][val]
            else:
                file_df.loc[i, col] = type_func(val)
                key_dict[col][val] = file_df.loc[i, col]
    
    datetime_str = datetime.now().strftime("%Y%m%d%H%M%S")
    archive_dir = active_dir / "archive" / datetime_str
    archive_dir.mkdir(parents=True, exist_ok=True)
    
    shutil.copytree(config_dir, archive_dir / config_dir.name)
    shutil.copytree(keydb_dir, archive_dir / keydb_dir.name)
    
    for k, v in key_dict.items():
        save_json(keydb_dir / f"{k}.json", v)
    
    save_path = active_dir / "files" / f"{Path(filepath).stem}_deidentified-{datetime_str}.csv"
    file_df.to_csv(save_path, index=False)
    
    logging.info(f"Deidentification complete. Input: {Path(filepath).resolve()} Output: {Path(save_path).resolve()}")
