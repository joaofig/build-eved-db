# build-eved-db

The code in this repository builds an SQLite database with the contents of the Extended Vehicle Energy Dataset.


# Usage

## Initialization

This repository uses the [uv](https://docs.astral.sh/uv/) Python package manager.
Please install it on your local machine before proceeding.

After cloning the repository, run the following from the command line: 

```shell
uv sync
```

This will create the virtual environment and install the required dependencies.

To build the initial version of the database, run the following from the command line:

```shell
make download-data
make build-signals
```

The target database named `eved.db` is generated to the local `data` folder.
It is a relatively large file with approximately 4 GiB in size.

## Map-Matching

The map-matching process generates polylines for each trip using the map 
nodes of the map-matched segments.
Before running the map-matching process, you need to install `docker` or
a similar containerization tool. In this project, we used `podman` as
an alternative to `docker`.
The container uses an open-source map matching engine called `valhalla`
with a community-based image.
Map information is sourced from `geofabrik` using their 
[Michigan](https://download.geofabrik.de/north-america/us/michigan-latest.osm.pbf)
extract.
Download the extract file and place it in the `/valhalla/custom_files` folder.
Once done, run the following from the command line:

```shell
make docker-run
```

or

```shell
make podman-run
```

This will start the container and run the `valhalla` process.
Note that the initialization process may take a while, depending
on the size of your extract and you computer's performance.
When ready, run the following from the command line:

```shell
make build-nodes
```

This will generate the map-matched nodes for each trajectory.
Note that there is not a one-to-one mapping between trajectories 
points and map nodes.
The map nodes reflect the map's geography vertices, while the points
in the `signals` table reflect the sampled noisy GPS vehicle locations
and their projections to the map's edges.
Again, this process may take a while to run.
