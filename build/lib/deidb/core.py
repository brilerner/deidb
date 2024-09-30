from datetime import datetime
import pandas as pd
import shutil
from pathlib import Path
import logging

from deidb import type_functions
from deidb.utils import (
    load_yaml,
    save_json,
    setup_logging,
    make_key_dict,
    validate_config,
)


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

        for i, val in enumerate(file_df[col]):
            if val in key_dict[col]:
                file_df.loc[i, col] = key_dict[col][val]
            else:
                type_func = getattr(type_functions, config["included"][col]["function"])
                # PUT ADDITONAL CHECKS
                file_df.loc[i, col] = type_func(val)
                key_dict[col][val] = file_df.loc[i, col]

    datetime_str = datetime.now().strftime("%Y%m%d%H%M%S")
    archive_dir = active_dir / "archive" / datetime_str
    archive_dir.mkdir(parents=True, exist_ok=True)

    shutil.copytree(config_dir, archive_dir / config_dir.name)
    shutil.copytree(keydb_dir, archive_dir / keydb_dir.name)

    for k, v in key_dict.items():
        save_json(keydb_dir / f"{k}.json", v)

    save_path = (
        active_dir / "files" / f"{Path(filepath).stem}_deidentified-{datetime_str}.csv"
    )
    file_df.to_csv(save_path, index=False)

    logging.info(
        f"Deidentification complete. Input: {Path(filepath).resolve()} Output: {Path(save_path).resolve()}"
    )
