import json
from pathlib import Path

from fire import Fire
from appdirs import user_config_dir

__version__ = "0.0.1"
_appdata_dir = Path(user_config_dir(appname="tit", appauthor="tit"))
CONFIG_PATH = _appdata_dir / Path("tit_config.json")


def version():
    print(__version__)


def prompt():
    print(f"Prompt located at {CONFIG_PATH}")
    print(json.loads(CONFIG_PATH.read_text())["prompt"])
    raise NotImplementedError("Not implemented")


def commit():
    print(f"Commit message: ")
    raise NotImplementedError("Not implemented")


def init_cli():
    Fire(
        {
            "commit": commit,
            "prompt": prompt,
            "--version": version,
            "-v": version,
        }
    )
