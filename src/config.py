from pathlib import Path
from typing import Dict

import tomli


def load_config() -> Dict:
    return tomli.loads(Path("./config.toml").read_text(encoding="utf-8"))
