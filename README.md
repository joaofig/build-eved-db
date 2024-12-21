# build-eved-db

The code in this repository builds an SQLite database with the contents of the Extended Vehicle Energy Dataset.


# Usage

## Initialization

This repository uses the [uv](https://docs.astral.sh/uv/) Python package manager.
Please install it on your local machine before proceeding.

To initialize the local environment, run the following from the command line:

```shell
make init
```

To build the initial version of the database, run the following from the command line:

```shell
make download-data
make build
```