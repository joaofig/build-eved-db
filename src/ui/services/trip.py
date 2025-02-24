from typing import List, Tuple

from src.db.EvedDb import EvedDb


def get_gps_trajectory(traj_id: int) -> List[Tuple[float, float]]:
    db = EvedDb()
    sql = """
    select      s.latitude
    ,           s.longitude
    from        signal s
    inner join  trajectory t on s.trip_id = t.trip_id and s.vehicle_id = t.vehicle_id
    where       t.traj_id = ?
    """
    return db.query(sql, parameters=[traj_id])


def get_match_trajectory(traj_id: int) -> List[Tuple[float, float]]:
    db = EvedDb()
    sql = """
    select      s.match_latitude
    ,           s.match_longitude
    from        signal s
    inner join  trajectory t on s.trip_id = t.trip_id and s.vehicle_id = t.vehicle_id
    where       t.traj_id = ?
    """
    return db.query(sql, parameters=[traj_id])
