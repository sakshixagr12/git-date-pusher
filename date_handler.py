# Pure core date handling (no UI)
import datetime
from typing import List
from rich.prompt import Prompt
from rich.console import Console

console = Console()

def _format_noon(date_obj: datetime.date) -> str:
    """Return a datetime string for the given date at 12:00:00.

    Args:
        date_obj: The date to format.
    Returns:
        A string in the form ``YYYY-MM-DD 12:00:00``.
    """
    return f"{date_obj.isoformat()} 12:00:00"


def get_today_str() -> str:
    """Return today's date at noon (``YYYY-MM-DD 12:00:00``)."""
    return _format_noon(datetime.date.today())
def get_valid_datetime(prompt_msg: str) -> str:
    """Prompt for a date and optional time, returning ``YYYY-MM-DD HH:MM:SS``.

    The function repeatedly asks until both inputs are valid. If the time
    input is left blank, it defaults to ``12:00:00``.
    """
    while True:
        date_str = Prompt.ask(f"{prompt_msg} (date YYYY-MM-DD)")
        try:
            _parse_date(date_str)
        except ValueError:
            console.print("[red]Invalid date format. Use YYYY-MM-DD.[/red]")
            continue

        time_str = Prompt.ask(f"{prompt_msg} (time HH:MM:SS, optional)", default="12:00:00")
        if not time_str:
            time_str = "12:00:00"
        try:
            _parse_time(time_str)
        except ValueError:
            console.print("[red]Invalid time format. Use HH:MM:SS.[/red]")
            continue

        return f"{date_str} {time_str}"

def _parse_date(date_str: str) -> datetime.date:
    """Parse a ``YYYY-MM-DD`` string into a :class:`datetime.date`.

    Raises:
        ValueError: If the string is not a valid date.
    """
    return datetime.datetime.strptime(date_str, "%Y-%m-%d").date()


def _parse_time(time_str: str) -> datetime.time:
    """Parse a ``HH:MM:SS`` string into a :class:`datetime.time`.

    Raises:
        ValueError: If the string is not a valid time.
    """
    return datetime.datetime.strptime(time_str, "%H:%M:%S").time()


def generate_date_schedule(start: str, end: str, count: int) -> List[str]:
    """Generate an evenly spaced list of commit timestamps.

    Parameters
    ----------
    start: str
        Start date in ``YYYY-MM-DD`` format.
    end: str
        End date in ``YYYY-MM-DD`` format.
    count: int
        Number of timestamps to generate.

    Returns
    -------
    List[str]
        List of timestamps formatted as ``YYYY-MM-DD HH:MM:SS`` where the
        time component defaults to ``12:00:00``.
    """
    if count < 1:
        raise ValueError("Count must be at least 1")
    try:
        start_dt = _parse_date(start)
        end_dt = _parse_date(end)
    except ValueError as exc:
        raise ValueError("Start and end dates must be in YYYY-MM-DD format") from exc
    if end_dt < start_dt:
        raise ValueError("End date must be on or after start date")
    total_days = (end_dt - start_dt).days
    if count == 1:
        return [_format_noon(start_dt)]
    step = total_days / (count - 1)
    schedule = []
    for i in range(count):
        delta = round(step * i)
        cur_date = start_dt + datetime.timedelta(days=delta)
        schedule.append(_format_noon(cur_date))
    return schedule
