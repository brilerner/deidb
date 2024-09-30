from setuptools import setup, find_packages

setup(
    name="deidb",
    version="0.1",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    entry_points={
        "console_scripts": [
            "deidb=deidb.cli:main",
        ],
    },
)
