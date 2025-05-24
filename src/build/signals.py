from typing import Tuple

import numpy as np
import pandas as pd

from os import remove
from zipfile import ZipFile
from tqdm import tqdm
from datetime import datetime, timedelta
from pytz import timezone
from src.common.geomath import vec_haversine
from src.db.EvedDb import EvedDb
import h3.api.numpy_int as h3


def remove_semi_colon(filename: str) -> None:
    with open(filename, "r") as f:
        data = f.read()
    data = data.replace(";", "")
    with open(filename, "w") as f:
        f.write(data)


def read_csv(filename: str) -> pd.DataFrame:
    columns = [
        "DayNum",
        "VehId",
        "Trip",
        "Timestamp(ms)",
        "Latitude[deg]",
        "Longitude[deg]",
        "Vehicle Speed[km/h]",
        "MAF[g/sec]",
        "Engine RPM[RPM]",
        "Absolute Load[%]",
        "OAT[DegC]",
        "Fuel Rate[L/hr]",
        "Air Conditioning Power[kW]",
        "Air Conditioning Power[Watts]",
        "Heater Power[Watts]",
        "HV Battery Current[A]",
        "HV Battery SOC[%]",
        "HV Battery Voltage[V]",
        "Short Term Fuel Trim Bank 1[%]",
        "Short Term Fuel Trim Bank 2[%]",
        "Long Term Fuel Trim Bank 1[%]",
        "Long Term Fuel Trim Bank 2[%]",
        "Elevation Raw[m]",
        "Elevation Smoothed[m]",
        "Gradient",
        "Energy_Consumption",
        "Matchted Latitude[deg]",
        "Matched Longitude[deg]",
        "Match Type",
        "Class of Speed Limit",
        "Speed Limit[km/h]",
        "Speed Limit with Direction[km/h]",
        "Intersection",
        "Bus Stops",
        "Focus Points",
    ]
    types = {
        "DayNum": float,
        "VehId": int,
        "Trip": int,
        "Timestamp(ms)": int,
        "Latitude[deg]": float,
        "Longitude[deg]": float,
        "Vehicle Speed[km/h]": float,
        "MAF[g/sec]": float,
        "Engine RPM[RPM]": float,
        "Absolute Load[%]": float,
        "OAT[DegC]": float,
        "Fuel Rate[L/hr]": float,
        "Air Conditioning Power[kW]": float,
        "Air Conditioning Power[Watts]": float,
        "Heater Power[Watts]": float,
        "HV Battery Current[A]": float,
        "HV Battery SOC[%]": float,
        "HV Battery Voltage[V]": float,
        "Short Term Fuel Trim Bank 1[%]": float,
        "Short Term Fuel Trim Bank 2[%]": float,
        "Elevation Raw[m]": float,
        "Elevation Smoothed[m]": float,
        "Gradient": float,
        "Energy_Consumption": float,
        "Matchted Latitude[deg]": float,
        "Matched Longitude[deg]": float,
        "Match Type": int,
        "Class of Speed Limit": float,
        "Speed Limit[km/h]": str,
        "Speed Limit with Direction[km/h]": float,
        "Intersection": float,
        "Bus Stops": float,
        "Focus Points": str,
    }
    df = pd.read_csv(filepath_or_buffer=filename,
                     usecols=np.array(columns),
                     dtype=types)
    return df



def get_trajectory_properties(traj_id: int) -> Tuple[float, float, datetime, datetime, int]:
    db = EvedDb()
    traj_df = db.get_trajectory(traj_id)
    points = traj_df[["match_latitude", "match_longitude"]].values
    length_m = vec_haversine(points[:-1, 0], points[:-1, 1],
                             points[1:, 0], points[1:, 1]).sum()
    base_dt = datetime(year=2017, month=11, day=1, tzinfo=timezone("America/Detroit"))
    day_num = traj_df["day_num"].iloc[0]
    dt_ini = base_dt + timedelta(days=day_num - 1) + timedelta(milliseconds=int(traj_df["time_stamp"].iloc[0]))
    dt_end = base_dt + timedelta(days=day_num - 1) + timedelta(milliseconds=int(traj_df["time_stamp"].iloc[-1]))
    return length_m, (dt_end - dt_ini).total_seconds(), dt_ini, dt_end, traj_id


def update_trajectories() -> None:
    db = EvedDb()
    df = db.get_trajectories()
    trajectories = df["traj_id"].tolist()

    props = [get_trajectory_properties(traj_id) for traj_id in tqdm(trajectories)]

    sql = """
    UPDATE      trajectory
    SET         length_m = ?
    ,           duration_s = ?
    ,           dt_ini = ?
    ,           dt_end = ?
    WHERE       traj_id = ?
    """
    db.execute_sql(sql, parameters=props, many=True)


def build_signals() -> None:
    db = EvedDb()

    if not db.table_exists("vehicle"):
        # Create vehicles
        db.ddl_script("sql/eved/create_vehicle.sql")
        vehicle_df = pd.concat([pd.read_excel("./data/VED_Static_Data_ICE&HEV.xlsx"),
                                pd.read_excel("./data/VED_Static_Data_PHEV&EV.xlsx")])
        vehicle_df = vehicle_df.replace("NO DATA", None)
        vehicles = [row for row in vehicle_df.itertuples(index=False)]
        db.insert_vehicles(vehicles)

    if not db.table_exists("signal"):
        # Create signals
        db.ddl_script("sql/eved/create_signal.sql")
        with ZipFile("data/eVED.zip", allowZip64=True) as zf:
            for zip_info in tqdm(list(zf.infolist())):
                zf.extract(zip_info, "data")
                remove_semi_colon(f"data/{zip_info.filename}")

                signal_df = read_csv(f"data/{zip_info.filename}")
                signal_df["h3_12"] = signal_df.apply(
                    lambda row: int(h3.latlng_to_cell(row["Matchted Latitude[deg]"],
                                                      row["Matched Longitude[deg]"], 12)),
                    axis=1)
                signals = [row for row in signal_df.itertuples(index=False)]
                db.insert_signals(signals)

                remove(f"data/{zip_info.filename}")


        db.ddl_script("sql/eved/create_signal_trip_index.sql")
        db.ddl_script("sql/eved/create_ix_signal_h3_12.sql")

    if not db.table_exists("trajectory"):
        db.create_trajectories()
        update_trajectories()
