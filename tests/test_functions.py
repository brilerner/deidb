import pytest
import pandas as pd
import yaml
import shutil
import importlib.resources

# Import your core functions
from deidb.core import deidentify_file
from deidb.utils import make_directory, make_key_dict

# Paths using importlib.resources
SAMPLE_DATA_DIR = (
    importlib.resources.files("deidb").parent.parent / "tests" / "sample_data"
)
INPUT_PATH = SAMPLE_DATA_DIR / "input_file.csv"
SAMPLE_IO_PATH = SAMPLE_DATA_DIR / "sample_io.yaml"
SAMPLE_ENV_DIR = SAMPLE_DATA_DIR / "env"
ENV_IO_PATH = SAMPLE_ENV_DIR / "config" / "io.yaml"


@pytest.fixture  # (scope="module" ; how/should this work?)
def setup_env():
    """Set up the environment for deidentification tests."""
    if SAMPLE_ENV_DIR.exists():
        shutil.rmtree(SAMPLE_ENV_DIR)

    make_directory(SAMPLE_ENV_DIR)
    shutil.copy(SAMPLE_IO_PATH, ENV_IO_PATH)

    yield SAMPLE_ENV_DIR

    # Teardown: Remove the environment directory after tests
    if SAMPLE_ENV_DIR.exists():
        shutil.rmtree(SAMPLE_ENV_DIR)


@pytest.fixture
def deid_output(setup_env):
    """Run the deidentification and load input/output data."""
    # Run deidentification
    deidentify_file(INPUT_PATH, setup_env)

    # Load data
    files_dir = setup_env / "files"
    keydb_dir = setup_env / "keydb"
    filepath_out = next(files_dir.iterdir())

    df_out = pd.read_csv(filepath_out)
    df_in = pd.read_csv(INPUT_PATH)

    with open(ENV_IO_PATH, "r") as file:
        config = yaml.safe_load(file)
    key_dict = make_key_dict(config, keydb_dir)

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
    """Test that the output columns match the input columns."""
    assert list(df_in.columns) == list(df_out.columns)


def test_deidentified_columns_changed(df_in, df_out, config):
    """Ensure that values in columns marked for deidentification have changed."""
    for col in config["included"]:
        if col in df_in.columns:
            assert all(df_in[col] != df_out[col])


def test_excluded_columns_unchanged(df_in, df_out, config):
    """Ensure that values in columns marked for exclusion remain unchanged."""
    for col in config["excluded"]:
        if col in df_in.columns:
            assert all(df_in[col] == df_out[col])


def test_keydb_validity(df_in, df_out, key_dict, config):
    """Test that the original values can be recovered using the keydb."""
    for col in config["included"]:
        if col in df_in.columns:
            recovered_col = df_out[col].replace(
                {v: k for k, v in key_dict[col].items()}
            )
            assert all(recovered_col == df_in[col])
