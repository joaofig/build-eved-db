from os import path

from src.config import load_config
from src.db.api import BaseDb


class MatchDb(BaseDb):
    def __init__(self):
        config = load_config()
        database = config.get("database")
        filename = path.join(
            database.get("folder", "./data/eved_match.db"),
            database.get("eved_match", "eved_match.db"),
        )
        super().__init__(db_name=filename)

    def create_node(self):
        self.ddl_script("sql/eved_match/create_node.sql")
        self.ddl_script("sql/eved_match/create_ix_node_traj_id.sql")
        self.ddl_script("sql/eved_match/create_ix_node_h3_12.sql")