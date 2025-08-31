import json
from pathlib import Path

from fire import Fire
from appdirs import user_config_dir

__version__ = "0.0.2"
_appdata_dir = Path(user_config_dir(appname="giz", appauthor="giz"))
CONFIG_PATH = _appdata_dir / Path("giz_config.json")


def version():
    print(__version__)


def config():
    print(f"config located at {CONFIG_PATH}")


def commit():
    print(f"Commit message: ")
    raise NotImplementedError("Not implemented")


def init_cli():
    Fire(
        {
            "commit": commit,
            "config": config,
            "--version": version,
            "-v": version,
        }
    )
