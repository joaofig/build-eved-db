from typing import List, Tuple

import pandas as pd

from src.db.EvedDb import EvedDb
from valhalla import Actor, get_config
from valhalla.utils import decode_polyline
import h3.api.numpy_int as h3


def map_match(actor: Actor,
              df: pd.DataFrame) -> str:
    param = {
        "use_timestamps": True,
        "shortest": True,
        "shape_match": "walk_or_snap",
        "shape": df.to_dict(orient='records'),
        "costing": "auto",
        "format": "osrm",
        "directions_options": {
            "directions_type": "none"
        },
        "trace_options": {
            "search_radius": 50,
            "max_search_radius": 200,
            "gps_accuracy": 10,
            "breakage_distance": 2000,
            "turn_penalty_factor": 1
        },
        "costing_options": {
            "auto": {
                "country_crossing_penalty": 2000.0,
                "maneuver_penalty": 30
            }
        }
    }
    route = actor.trace_route(param)
    return route["matchings"][0]["geometry"]


def get_trajectories() -> pd.DataFrame:
    db = EvedDb()
    return db.get_trajectories()


def load_trajectory_points(traj_id: int) -> pd.DataFrame:
    db = EvedDb()

    sql = f"""
    select     distinct
               s.latitude as lat
    ,          s.longitude as lon
    ,          min(s.time_stamp) / 1000 as time
    from       signal s
    inner join trajectory t on s.vehicle_id = t.vehicle_id and s.trip_id = t.trip_id
    where      t.traj_id = ?
    group by   s.latitude, s.longitude;
    """
    return db.query_df(sql, [traj_id]).sort_values(by=["time"])


def insert_nodes(traj_id: int, nodes: List[Tuple[float, float]]) -> None:
    db = EvedDb()
    sql = "insert into node (traj_id, latitude, longitude, h3_12) values (?, ?, ?, ?)"
    params = [(traj_id, lat, lon, h3.latlng_to_cell(lat, lon, 12))
              for (lat, lon) in nodes
              if lat is not None and lon is not None]
    db.execute_sql(sql, params, many=True)


def insert_error(traj_id: int,
                 error: str) -> None:
    db = EvedDb()

    sql = "insert into node (traj_id, match_error) values (?, ?)"
    db.execute_sql(sql, [traj_id, error])


def build_nodes() -> None:
    db = EvedDb()

    if not db.table_exists("node"):
        tiles = './valhalla/custom_files/valhalla_tiles.tar'
        config = get_config(tile_extract=tiles, verbose=True)
        db.create_node()

        traj_df = get_trajectories()
        for traj_id in traj_df["traj_id"].to_list():
            actor = Actor(config)

            print(traj_id)
            try:
                traj_df = load_trajectory_points(traj_id)
                geometry = map_match(actor, traj_df)

                if geometry is not None:
                    nodes = decode_polyline(geometry)[1:-1]
                    insert_nodes(traj_id, nodes)
            except RuntimeError as e:
                insert_error(traj_id, str(e))
                print(e)




