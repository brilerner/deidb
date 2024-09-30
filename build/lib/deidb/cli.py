import argparse
import os
from deidb.core import deidentify_file
from deidb.utils import make_directory, get_active_directory, get_activated_directories
from pathlib import Path


def file_choices(choices, filename):
    """Ensure the file has the correct extension."""
    ext = os.path.splitext(filename)[1][1:]  # Extract file extension without the dot
    if ext not in choices:
        raise argparse.ArgumentTypeError(f"File must end with one of {choices}")
    return filename


def check_path(path):
    """Ensure the path is a directory."""
    # If the path is not a root directory, check if it exists and make the path go from the current directory
    path = Path(path)
    if not path.is_absolute():
        path = Path.cwd() / path
    # check if the path exists in the list of previous directories
    if path.exists() and path not in get_activated_directories():
        raise argparse.ArgumentTypeError(f"{path} is not an activated deidb directory")
    # check if the path is a directory (check whether there is a file suffix)
    if path.suffix:
        raise argparse.ArgumentTypeError(f"{path} is not a directory")

    return path


def parse_arguments():
    """Parse command-line arguments for the CLI tool."""
    parser = argparse.ArgumentParser(description="deidb: command-line EHR deidentifier")

    # Create subparsers for "activate" and "deid" commands
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Parser for the "activate" command
    parser_activate = subparsers.add_parser(
        "activate", help="Activate a deidb database directory"
    )
    parser_activate.add_argument(
        "directory",
        type=check_path,
        help="Name of the directory to activate",
    )

    # Parser for the "deid" command
    parser_deid = subparsers.add_parser("deid", help="Deidentify a CSV file")
    parser_deid.add_argument(
        "filepath",
        type=lambda s: file_choices(("csv",), s),  # Ensure file is a CSV
        help="Path to the CSV file to deidentify",
    )

    return parser.parse_args()


def main():
    args = parse_arguments()

    # Handle the different commands
    if args.command == "activate":
        make_directory(args.directory)
        print(f"Directory '{args.directory}' activated.")
    elif args.command == "deid":
        active_dir = get_active_directory()
        print("Active directory:", active_dir)
        deidentify_file(args.filepath, active_dir)
    else:
        raise ValueError("Invalid command")


if __name__ == "__main__":
    main()
