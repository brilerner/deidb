# deidb

A command-line tool for de-identifying Electronic Health Records (EHR) data in CSV files. It replaces sensitive identifier columns with randomly generated substitutes while maintaining a reversible key database for potential re-identification.

## Features

- **CSV De-identification**: Reads CSV files and de-identifies specified columns while preserving column structure
- **Persistent Key Database**: Maintains JSON-based key mappings enabling consistent de-identification across multiple files
- **Configuration-Driven**: YAML-based configuration specifies which columns to include/exclude
- **Reversible**: Stored keys enable potential re-identification when needed
- **Audit Trail**: Logs all operations and archives previous configurations

## Installation

```bash
# Clone the repository
git clone https://github.com/brilerner/deidb.git
cd deidb

# Install dependencies
pip install pandas pyyaml

# Install the package
pip install -e .
```

## Quick Start

### 1. Activate a working directory

```bash
deidb activate /path/to/project
```

This creates the following structure:
```
/path/to/project/
├── config/    # Configuration files (io.yaml)
├── keydb/     # Key database storage
├── files/     # Output files
└── logs/      # Operation logs
```

### 2. Configure columns to de-identify

Edit `config/io.yaml` in your activated directory:

```yaml
# Columns to pass through unchanged
excluded:
  - info
  - other_non_sensitive_column

# Columns to de-identify
included:
  id:
    function: random_number_substitution
  patient_id:
    function: random_number_substitution
    kwargs:
      padded_length: 12
```

### 3. De-identify a file

```bash
deidb deid /path/to/input.csv
```

Output is saved as `<original_name>_deidentified-<timestamp>.csv` in the `files/` directory.

## CLI Commands

| Command | Description |
|---------|-------------|
| `deidb activate <directory>` | Set up a de-identification environment |
| `deidb deid <csv_file>` | De-identify a CSV file using the active directory |

## Configuration

The `io.yaml` configuration file specifies:

- **excluded**: Column names to pass through unchanged
- **included**: Columns to de-identify, with their transformation function and optional kwargs

### Available Transformation Functions

| Function | Description |
|----------|-------------|
| `random_number_substitution` | Replaces digits with random digits, pads to specified length (default: 10) |

## How It Works

1. **Activation**: Creates a working environment with required subdirectories and default config
2. **De-identification**: 
   - Validates config against input columns
   - For each value in included columns: uses existing key if available, otherwise generates a new random substitution
   - Saves de-identified output and updates key database
   - Archives config and keydb with timestamp

## Output

After de-identification:

```
<activated_dir>/
├── config/io.yaml                              # Configuration
├── keydb/<column_name>.json                    # Key mappings per column
├── files/<name>_deidentified-<timestamp>.csv   # De-identified output
├── logs/deidentify_file.log                    # Operation log
└── archive/<timestamp>/                        # Archived snapshots
```

## Testing

```bash
pytest tests/
```

## Requirements

- Python 3.11+
- pandas
- pyyaml

## License

See repository for license information.
