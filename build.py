from typing import List, Tuple

import pandas as pd

from zipfile import ZipFile
from os import remove
from src.db.api import BaseDb
from tqdm import tqdm


class Db(BaseDb):
    def __init__(self):
        super().__init__(db_name="./data/eved.sqlite")

    def ddl_script(self, filename: str) -> None:
        with open(filename, "r") as f:
            sql = f.read()
            self.execute_sql(sql)

    def insert_list(self, filename: str, values: List[Tuple]) -> None:
        conn = self.connect()
        cur = conn.cursor()

        with open(filename, "r") as f:
            sql = f.read()
            cur.executemany(sql, values)

        conn.commit()
        cur.close()
        conn.close()

    def insert_signals(self, signals):
        self.insert_list("sql/insert_signal.sql", signals)


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
    return pd.read_csv(filename, usecols=columns, dtype=types)


def main():
    db = Db()

    db.ddl_script("sql/create_signal.sql")

    with ZipFile("data/eVED.zip", allowZip64=True) as zf:
        for zip_info in tqdm(zf.infolist()):
            zf.extract(zip_info, "data")
            remove_semi_colon(f"data/{zip_info.filename}")

            df = read_csv(f"data/{zip_info.filename}")
            signals = [row for row in df.itertuples(index=False)]
            db.insert_signals(signals)

            remove(f"data/{zip_info.filename}")

    db.ddl_script("sql/create_signal_trip_index.sql")


if __name__ == "__main__":
    main()
