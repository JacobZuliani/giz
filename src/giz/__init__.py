import json
import sys
import textwrap
import subprocess
from pathlib import Path

from fire import Fire
from openai import OpenAI
from yaspin import yaspin
from platformdirs import user_config_dir

__version__ = "1.0.0"

CONFIG_PATH = Path(user_config_dir("giz")) / "giz_config.json"
CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
CONFIG_PATH.touch(exist_ok=True)
model = json.loads(CONFIG_PATH.read_text() or "{}").get("model", "gpt-5-nano")
openai_api_key = json.loads(CONFIG_PATH.read_text() or "{}").get("openai_api_key", "")
CONFIG_PATH.write_text(json.dumps({"openai_api_key": openai_api_key, "model": model}))

PROMPT_PATH = Path(user_config_dir("giz")) / "giz_prompt"
PROMPT_PATH.parent.mkdir(parents=True, exist_ok=True)
PROMPT_PATH.touch(exist_ok=True)
if not PROMPT_PATH.read_text():
    prompt = "Generate me a very concise, short commit message from the following git diff:"
    PROMPT_PATH.write_text(prompt)

USAGE = """
giz: `git commit` with an AI commit message.

Usage:
  giz commit [flags...]
  giz set_openai_api_key <key>
  giz promptfile
  giz configfile
  giz --version | -v

"""


def version():
    print(__version__)


def print_promptfile_path():
    print(f'Promptfile path: "{PROMPT_PATH}"')


def print_configfile_path():
    print(f'Configfile path: "{CONFIG_PATH}"')


def set_api_key(value: str):
    config = json.loads(CONFIG_PATH.read_text())
    config["openai_api_key"] = value
    try:
        messages = [{"role": "user", "content": "Hello"}]
        OpenAI(api_key=value).chat.completions.create(model="gpt-5-nano", messages=messages)
        CONFIG_PATH.write_text(json.dumps(config))
        print(f"API key updated successfully!")
    except Exception as e:
        print(f"Error testing API key!\n{e}")


def _collect_passthrough_arguments():
    index = sys.argv.index("commit") if "commit" in sys.argv else len(sys.argv)
    user_arguments = sys.argv[index + 1 :]

    yes_flag = False
    skip_next = False
    forwarded_arguments = []
    for argument in user_arguments:
        if skip_next:
            skip_next = False
        elif argument in ("-y", "--yes"):
            yes_flag = True
        elif argument in ("-m", "--message"):
            skip_next = True
        elif not argument.startswith("--message="):
            forwarded_arguments.append(argument)

    return yes_flag, forwarded_arguments


def commit(yes: bool = False):
    """
    Same as `git commit` but with an AI commit message.

    Usage:
      giz commit [flags...]

    Args:
      -y, --yes        Auto-accept the AI commit message.
      other flags      Passed through to `git commit` (e.g. --amend, --no-verify, -S).
    """
    config = json.loads(CONFIG_PATH.read_text())
    if not config.get("openai_api_key"):
        print(f"API key not set. Please set API key first with: `giz set_openai_api_key <api_key>`")
        return

    cmd = ["git", "diff", "--staged"]
    diff_text = subprocess.run(cmd, stdout=subprocess.PIPE, text=True, check=True).stdout
    if not diff_text:
        print("No staged changes to commit.")
        return

    with yaspin() as spinner:
        spinner.start()
        client = OpenAI(api_key=config["openai_api_key"])
        system_message = {"role": "system", "content": "You are a commit message generator."}
        user_messsage = {"role": "user", "content": f"{PROMPT_PATH.read_text()}\n\n{diff_text}"}
        messages = [system_message, user_messsage]
        response = client.chat.completions.create(model=config["model"], messages=messages)
    commit_message = response.choices[0].message.content.strip()
    print(f"\n{commit_message}\n")

    yes_flag, forwarded_arguments = _collect_passthrough_arguments()
    commit_command = ["git", "commit", "-m", commit_message, *forwarded_arguments]

    if yes_flag:
        subprocess.run(commit_command, check=True)
    else:
        confirmation = input("Would you like to commit? [Y/n]: ").strip().lower()
        if confirmation in ("", "y", "yes"):
            subprocess.run(commit_command, check=True)
        else:
            print("Aborted.")


def init_cli():
    argv = sys.argv[1:]
    if not argv or argv[0] in ("help", "-h", "--help"):
        print(USAGE)
    elif argv[0] == "commit" and any(a in ("-h", "--help") for a in argv[1:]):
        print(textwrap.dedent(commit.__doc__))
    else:
        Fire(
            {
                "commit": commit,
                "set_openai_api_key": set_api_key,
                "configfile": print_configfile_path,
                "promptfile": print_promptfile_path,
                "--version": version,
                "-v": version,
            }
        )
