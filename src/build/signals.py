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


def read_csv_chunked(filename: str, chunk_size: int = 10000):
    """Read CSV file in chunks for better memory efficiency."""
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
        "DayNum": np.float32,
        "VehId": np.int32,
        "Trip": np.int32,
        "Timestamp(ms)": np.int64,
        "Latitude[deg]": np.float64,
        "Longitude[deg]": np.float64,
        "Vehicle Speed[km/h]": np.float32,
        "MAF[g/sec]": np.float32,
        "Engine RPM[RPM]": np.float32,
        "Absolute Load[%]": np.float32,
        "OAT[DegC]": np.float32,
        "Fuel Rate[L/hr]": np.float32,
        "Air Conditioning Power[kW]": np.float32,
        "Air Conditioning Power[Watts]": np.float32,
        "Heater Power[Watts]": np.float32,
        "HV Battery Current[A]": np.float32,
        "HV Battery SOC[%]": np.float32,
        "HV Battery Voltage[V]": np.float32,
        "Short Term Fuel Trim Bank 1[%]": np.float32,
        "Short Term Fuel Trim Bank 2[%]": np.float32,
        "Elevation Raw[m]": np.float32,
        "Elevation Smoothed[m]": np.float32,
        "Gradient": np.float32,
        "Energy_Consumption": np.float32,
        "Matchted Latitude[deg]": np.float64,
        "Matched Longitude[deg]": np.float64,
        "Match Type": np.float32,
        "Class of Speed Limit": np.float32,
        "Speed Limit[km/h]": str,
        "Speed Limit with Direction[km/h]": np.float32,
        "Intersection": np.float32,
        "Bus Stops": np.float32,
        "Focus Points": str,
    }
    
    # Use chunked reading for memory efficiency
    chunk_reader = pd.read_csv(
        filepath_or_buffer=filename,
        usecols=columns,
        dtype=types,
        chunksize=chunk_size,
        low_memory=True
    )
    return chunk_reader


def read_csv(filename: str) -> pd.DataFrame:
    """Fallback function for backward compatibility."""
    chunk_reader = read_csv_chunked(filename, chunk_size=50000)
    return pd.concat(chunk_reader, ignore_index=True)


def get_trajectory_properties(traj_id: int) -> Tuple[float, float, datetime, datetime, int, int, int]:
    db = EvedDb()
    traj_df = db.get_trajectory(traj_id)
    
    if traj_df.empty:
        return 0.0, 0.0, datetime.now(), datetime.now(), 0, 0, traj_id
    
    points = traj_df[["match_latitude", "match_longitude"]].values
    
    # Vectorized distance calculation
    if len(points) > 1:
        length_m = vec_haversine(points[:-1, 0], points[:-1, 1],
                                 points[1:, 0], points[1:, 1]).sum()
    else:
        length_m = 0.0
    
    base_dt = datetime(year=2017, month=11, day=1, tzinfo=timezone("America/Detroit"))
    day_num = traj_df["day_num"].iloc[0]
    
    dt_ini = base_dt + timedelta(days=day_num - 1) + timedelta(milliseconds=int(traj_df["time_stamp"].iloc[0]))
    dt_end = base_dt + timedelta(days=day_num - 1) + timedelta(milliseconds=int(traj_df["time_stamp"].iloc[-1]))
    
    # Vectorized H3 calculations
    first_lat, first_lon = traj_df["match_latitude"].iloc[0], traj_df["match_longitude"].iloc[0]
    last_lat, last_lon = traj_df["match_latitude"].iloc[-1], traj_df["match_longitude"].iloc[-1]
    
    h3_ini = h3.latlng_to_cell(first_lat, first_lon, 12) if not (np.isnan(first_lat) or np.isnan(first_lon)) else 0
    h3_end = h3.latlng_to_cell(last_lat, last_lon, 12) if not (np.isnan(last_lat) or np.isnan(last_lon)) else 0
    
    return length_m, (dt_end - dt_ini).total_seconds(), dt_ini, dt_end, int(h3_ini), int(h3_end), traj_id


def update_trajectories() -> None:
    from concurrent.futures import ThreadPoolExecutor, as_completed
    import multiprocessing
    
    db = EvedDb()
    df = db.get_trajectories()
    trajectories = df["traj_id"].tolist()
    
    # Use parallel processing for trajectory property calculation
    max_workers = min(multiprocessing.cpu_count(), 8)
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all tasks
        future_to_traj = {executor.submit(get_trajectory_properties, traj_id): traj_id for traj_id in trajectories}
        
        props = []
        for future in tqdm(as_completed(future_to_traj), total=len(trajectories), desc="Processing trajectories"):
            try:
                result = future.result()
                props.append(result)
            except Exception as e:
                traj_id = future_to_traj[future]
                print(f"Error processing trajectory {traj_id}: {e}")
    
    # Batch update with a larger batch size
    sql = """
    UPDATE      trajectory
    SET         length_m = ?
    ,           duration_s = ?
    ,           dt_ini = ?
    ,           dt_end = ?
    ,           h3_12_ini = ?
    ,           h3_12_end = ?
    WHERE       traj_id = ?
    """
    db.execute_sql(sql, parameters=props, many=True, batch_size=2000)


def build_signals() -> None:
    db = EvedDb()

    if not db.table_exists("vehicle"):
        # Create vehicles
        db.ddl_script("sql/eved/create_vehicle.sql")
        vehicle_df = pd.concat([pd.read_excel("./data/VED_Static_Data_ICE&HEV.xlsx"),
                                pd.read_excel("./data/VED_Static_Data_PHEV&EV.xlsx")])
        vehicle_df = vehicle_df.replace("NO DATA", None)
        vehicles = [tuple(row) for row in vehicle_df.itertuples(index=False)]
        db.insert_vehicles(vehicles)

    if not db.table_exists("signal"):
        # Create signals
        db.ddl_script("sql/eved/create_signal.sql")
        with ZipFile("data/eVED.zip", allowZip64=True) as zf:
            for zip_info in tqdm(list(zf.infolist())):
                zf.extract(zip_info, "data")
                remove_semi_colon(f"data/{zip_info.filename}")

                # Process file in chunks for better memory efficiency
                chunk_reader = read_csv_chunked(f"data/{zip_info.filename}", chunk_size=25000)
                
                for chunk_df in chunk_reader:
                    # Vectorized H3 calculation - much faster than apply()
                    lats = chunk_df["Matchted Latitude[deg]"].values
                    lons = chunk_df["Matched Longitude[deg]"].values

                    h3_cells = np.zeros(len(lats), dtype=np.int64)
                    
                    for i, (lat, lng) in enumerate(zip(lats, lons)):
                        if not np.isnan(lat) and not np.isnan(lng):
                            h3_cells[i] = h3.latlng_to_cell(lats[i], lons[i], 12)

                    chunk_df["h3_12"] = h3_cells
                    signals = [row for row in chunk_df.itertuples(index=False)]
                    db.insert_signals(signals)
                    
                    # Clear memory
                    del chunk_df, signals

                remove(f"data/{zip_info.filename}")


        db.ddl_script("sql/eved/create_signal_trip_index.sql")
        db.ddl_script("sql/eved/create_ix_signal_h3_12.sql")

    if not db.table_exists("trajectory"):
        db.create_trajectories()
        update_trajectories()
