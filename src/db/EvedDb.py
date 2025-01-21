import pandas as pd

from os import path
from typing import List, Tuple
from src.config import load_config
from src.db.api import BaseDb


class EvedDb(BaseDb):
    def __init__(self):
        config = load_config()
        database = config.get("database")
        filename = path.join(
            database.get("folder", "./data/eved.db"),
            database.get("eved", "eved.sqlite")
        )
        super().__init__(db_name=filename)

    def insert_vehicles(self, vehicles):
        self.insert_list("sql/eved/insert_vehicle.sql", vehicles)

    def insert_signals(self, signals):
        self.insert_list("sql/eved/insert_signal.sql", signals)

    def create_trajectories(self):
        self.ddl_script("sql/eved/create_trajectory.sql")
        self.ddl_script("sql/eved/insert_trajectories.sql")
        self.ddl_script("sql/eved/create_trajectory_vehicle_index.sql")

    def get_trajectories(self) -> List[int]:
        sql = "SELECT traj_id FROM trajectory"
        return [r[0] for r in self.query(sql)]

    def get_vehicles(self) -> pd.DataFrame:
        sql = "SELECT vehicle_id, vehicle_type, vehicle_class FROM vehicle"
        return self.query_df(sql)
