import json
import subprocess
from pathlib import Path
from typing import Any, Optional

import typer
from typer import Context, Option
from openai import OpenAI
from platformdirs import user_config_dir
from yaspin import yaspin

__version__ = "1.0.0"
app = typer.Typer(
    add_completion=False,
    context_settings={"help_option_names": ["-h", "--help"]},
    no_args_is_help=True,
)


CONFIG_PATH = Path(user_config_dir("giz")) / "giz_config.json"
CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
CONFIG_PATH.touch(exist_ok=True)
config_value = json.loads(CONFIG_PATH.read_text() or "{}")
model_value = config_value.get("model", "gpt-5-mini")
api_key_value = config_value.get("openai_api_key", "")
CONFIG_PATH.write_text(json.dumps({"openai_api_key": api_key_value, "model": model_value}))

PROMPT_PATH = Path(user_config_dir("giz")) / "giz_prompt"
PROMPT_PATH.parent.mkdir(parents=True, exist_ok=True)
PROMPT_PATH.touch(exist_ok=True)
if not PROMPT_PATH.read_text():
    prompt = "Generate me a very concise, short commit message from the following git diff:"
    PROMPT_PATH.write_text(prompt)


COMMIT_HELP_MESSAGE = """
Drop-in `git commit` replacement with an AI commit message.

** EXTRA ARGS **\n
Any extra args are forwarded to `git commit` (e.g. --amend, --message, --no-verify, -S).
"""


@app.command(
    help=COMMIT_HELP_MESSAGE,
    context_settings={
        "allow_extra_args": True,
        "ignore_unknown_options": True,
        "help_option_names": ["-h", "--help"],
    },
)
def commit(
    ctx: Context,
    yes: bool = Option(False, "--yes", "-y", help="Auto-accept the AI commit message."),
    message: Optional[str] = Option(None, "--message", "-m", hidden=True),
):
    yes = yes or message
    config = json.loads(CONFIG_PATH.read_text() or "{}")
    if not config.get("openai_api_key"):
        print("API key not set. Set it with: `giz set_openai_api_key <api_key>`")
        raise typer.Exit(code=1)

    cmd = ["git", "diff", "--staged"]
    diff_text = subprocess.run(cmd, stdout=subprocess.PIPE, text=True, check=True).stdout
    if (not message) and diff_text:
        with yaspin():
            client = OpenAI(api_key=config["openai_api_key"])
            response = client.chat.completions.create(
                model=config["model"],
                messages=[
                    {"role": "system", "content": "You are a commit message generator."},
                    {"role": "user", "content": f"{PROMPT_PATH.read_text()}\n\n{diff_text}"},
                ],
            )
        message = response.choices[0].message.content.strip()
        print(f"\n{message}\n")

    if message:
        commit_command = ["git", "commit", "-m", message, *list(ctx.args)]
    else:
        commit_command = ["git", "commit", *list(ctx.args)]

    if yes or (not diff_text):
        subprocess.run(commit_command)
    else:
        confirmation = input("Would you like to commit? [Y/n]: ").strip().lower()
        if confirmation in ("", "y", "yes"):
            subprocess.run(commit_command)
        else:
            print("Aborted.")


@app.command("set_openai_api_key")
def set_api_key(value: str):
    config = json.loads(CONFIG_PATH.read_text() or "{}")
    config["openai_api_key"] = value
    try:
        messages = [{"role": "user", "content": "Hello"}]
        with yaspin(text="Testing API key..."):
            OpenAI(api_key=value).chat.completions.create(model="gpt-5-nano", messages=messages)
        CONFIG_PATH.write_text(json.dumps(config))
        print("API key updated successfully!")
    except Exception as error:
        print(f"Error testing API key!\n{error}")


@app.command("promptfile", help="Show path to file containing commit message prompt.")
def print_promptfile_path():
    print("\nThe result of `git diff --staged` is pasted two newlines below the prompt in:")
    print(f'"{PROMPT_PATH}"\n')


@app.command("configfile", help="Show path to file storing API key and preferred model.")
def print_configfile_path():
    print("\nYour API key and preferred model are stored in:")
    print(f'"{CONFIG_PATH}"\n')


def version_option_callback(value: bool):
    if value:
        print(__version__)
        raise typer.Exit()


@app.callback()
def _main(
    version: Optional[bool] = Option(
        None,
        "--version",
        "-v",
        help="Show version and exit.",
        callback=version_option_callback,
        is_eager=True,
    )
):
    return


def init_cli():
    app()
