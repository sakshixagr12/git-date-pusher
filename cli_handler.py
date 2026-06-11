import datetime
from rich.console import Console
from rich.prompt import Prompt


def get_valid_datetime(prompt_msg: str) -> str:
    """Prompt the user for a date and optional time, returning "YYYY-MM-DD HH:MM:SS".

    If time is omitted, defaults to "12:00:00". Re‑prompts until both inputs are valid.
    """
    console = Console()
    while True:
        date_input = Prompt.ask(f"{prompt_msg} (date YYYY-MM-DD)")
        try:
            datetime.datetime.strptime(date_input, "%Y-%m-%d")
        except ValueError:
            console.print("[red]Invalid date format. Use YYYY-MM-DD.[/red]")
            continue
        time_input = Prompt.ask("Enter time (HH:MM:SS, optional)", default="12:00:00")
        if not time_input:
            time_input = "12:00:00"
        try:
            datetime.datetime.strptime(time_input, "%H:%M:%S")
        except ValueError:
            console.print("[red]Invalid time format. Use HH:MM:SS.[/red]")
            continue
        return f"{date_input} {time_input}"
