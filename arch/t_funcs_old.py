import pytest
import pandas as pd
from pathlib import Path
import yaml
import shutil
import sys

# set up paths
root = Path(__file__).parent.parent
sample_data_dir = Path(__file__).parent / "sample_data"

input_path = sample_data_dir / "input_file.csv"
sample_io_path = sample_data_dir / "sample_io.yaml"
sample_env_dir = sample_data_dir / "env"
env_io_path = sample_env_dir / "config" / "io.yaml"

sys.path.append(str(root / "src"))


@pytest.fixture
def deid_output():
    from deidb.core import deidentify_file, make_directory, make_key_dict

    if sample_env_dir.exists():
        shutil.rmtree(sample_env_dir)

    # run the deidentification
    make_directory(sample_env_dir)
    shutil.copy(sample_io_path, env_io_path)
    deidentify_file(input_path, sample_env_dir)

    # set up paths
    files_dir = sample_env_dir / "files"
    keydb_dir = sample_env_dir / "keydb"
    filepath_out = next(files_dir.iterdir())
    io_path = sample_env_dir / "config" / "io.yaml"

    # load data
    df_out = pd.read_csv(filepath_out)
    df_in = pd.read_csv(input_path)
    key_dict = make_key_dict(list(keydb_dir.iterdir()))
    with open(io_path, "r") as file:
        config = yaml.safe_load(file)

    # then, delete the entire sample_env directory
    shutil.rmtree(sample_env_dir)

    return {"df_in": df_in, "df_out": df_out, "key_dict": key_dict, "config": config}


@pytest.fixture
def df_in(deid_output):
    return deid_output["df_in"]


@pytest.fixture
def df_out(deid_output):
    return deid_output["df_out"]


@pytest.fixture
def key_dict(deid_output):
    return deid_output["key_dict"]


@pytest.fixture
def config(deid_output):
    return deid_output["config"]


def test_column_name_consistency(df_in, df_out):
    assert all(df_in.columns == df_out.columns)


def test_changes(df_in, df_out, config):
    # make sure every value in the input has changed for columns that are included
    for col in config["included"]:
        if col in df_in.columns:
            assert all(df_in[col] != df_out[col])

    # make sure every value in the input is the same for columns that are excluded
    for col in config["excluded"]:
        if col in df_in.columns:
            assert all(df_in[col] == df_out[col])


def test_validity(df_in, df_out, key_dict, config):
    # test that the input data can be fully recovered from the output data using the keydb
    for col in config["included"]:
        if col in df_in.columns:
            assert all(df_in[col].replace(key_dict[col]) == df_out[col])
