from typing import List, Tuple
from tqdm import tqdm as tqdm

import pandas as pd
import requests

from src.db.EvedDb import EvedDb
import h3.api.numpy_int as h3


# decode an encoded string
def decode_polyline(encoded: str) -> List[Tuple[float, float]]:
    inv = 1.0 / 1e6
    decoded = []
    previous = [0, 0]
    i = 0
    # for each byte
    while i < len(encoded):
        # for each coord (lat, lon)
        ll = [0, 0]
        for j in [0, 1]:
            shift = 0
            byte = 0x20
            # keep decoding bytes until you have this coord
            while byte >= 0x20:
                byte = ord(encoded[i]) - 63
                i += 1
                ll[j] |= (byte & 0x1f) << shift
                shift += 5
            # get the final value adding the previous offset and remember it for the next
            ll[j] = previous[j] + (~(ll[j] >> 1) if ll[j] & 1 else (ll[j] >> 1))
            previous[j] = ll[j]
        # scale by the precision and chop off long coords also flip the positions so
        # it's the far more standard lon,lat instead of lat,lon
        decoded.append((float('%.6f' % (ll[0] * inv)), float('%.6f' % (ll[1] * inv))))
    # hand back the list of coordinates
    return decoded


def map_match(df: pd.DataFrame) -> str:
    param = {
        "use_timestamps": False,
        "shape_match": "map_snap",
        "costing": "auto",
        # "format": "json",
        "verbose": True,
        # "format": "osrm",
        # "directions_options": {
        #     "directions_type": "none"
        # },
        "shape": df.to_dict(orient="records"),
        # "linear_references": True,
        "trace_options": {
            "search_radius": 100,
        #     "max_search_radius": 200,
            "gps_accuracy": 10,
            # "breakage_distance": 2000,
            # "turn_penalty_factor": 1
        },
    }
    url = "http://localhost:8002/trace_route"
    headers = {'Content-type': 'application/json'}
    r = requests.post(url, json=param, headers=headers)
    if r.status_code != 200:
        raise RuntimeError(
            f"Error while calling Valhalla API: {r.status_code} - {r.text}"
        )
    route = r.json()
    return route["trip"]["legs"][0]["shape"]


def get_trajectories() -> pd.DataFrame:
    db = EvedDb()
    return db.get_trajectories()


def load_trajectory_points(traj_id: int) -> pd.DataFrame:
    db = EvedDb()

    sql = f"""
    select     --distinct
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
        db.create_node()
    else:
        db.delete_node()

    traj_df = get_trajectories()
    for traj_id in tqdm(traj_df["traj_id"].to_list()):
        try:
            traj_df = load_trajectory_points(traj_id)
            geometry = map_match(traj_df)

            if geometry is not None:
                nodes = decode_polyline(geometry) #[1:-1]
                insert_nodes(traj_id, nodes)
        except RuntimeError as e:
            insert_error(traj_id, str(e))
            print(e)
