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
make build-signals
```

The target database named `eved.db` is generated to the local `data` folder.
It is a relatively large file with approximately 4 GiB in size.

## Map-Matching

The map-matching process generates polylines for each trip using the map nodes of the map-matched segments.


```shell
make build-nodes
```
