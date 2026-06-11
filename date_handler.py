# Pure core date handling (no UI)
import calendar
import datetime
import re
from typing import List, Optional
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

def resolve_natural_date(input_str: str) -> datetime.datetime:
    """Resolve a natural language date string into a datetime object.
    
    Handles inputs like 'now', 'today', 'yesterday', 'last week', 
    '2 days ago', 'end of month'. Includes local timezone awareness.
    """
    s = input_str.strip().lower()
    
    # Get timezone-aware local time
    now = datetime.datetime.now().astimezone()
    noon_today = now.replace(hour=12, minute=0, second=0, microsecond=0)
    
    if s == "now":
        return now
    elif s == "today":
        return noon_today
    elif s == "yesterday":
        return noon_today - datetime.timedelta(days=1)
    elif s in ("last week", "last-week"):
        return noon_today - datetime.timedelta(days=7)
    elif s == "end of month":
        last_day = calendar.monthrange(now.year, now.month)[1]
        return noon_today.replace(day=last_day)
        
    match = re.match(r"^(\d+)\s+days?\s+ago$", s)
    if match:
        days = int(match.group(1))
        return noon_today - datetime.timedelta(days=days)
        
    raise ValueError(f"Unable to parse natural date: '{input_str}'")

def get_valid_datetime(prompt_msg: str, *, smart_flag: Optional[str] = None, default: Optional[str] = None) -> str:
    """Prompt for a date and optional time, or return a smart default.

    Parameters
    ----------
    prompt_msg : str
        Message displayed when falling back to manual input.
    smart_flag : Optional[str]
        One of '--now', '--today', '--yesterday', '--last-week'. If provided,
        the function returns the corresponding datetime string without prompting.
        Only a single flag should be supplied.
    default : Optional[str]
        Optional default date string for manual mode (used by tests).

    Returns
    -------
    str
        A datetime string in the format ``YYYY-MM-DD HH:MM:SS``.
    """
    # Smart Defaults Mode
    if smart_flag:
        flag_val = smart_flag.lstrip("-").replace("-", " ")
        try:
            dt = resolve_natural_date(flag_val)
            return dt.strftime("%Y-%m-%d %H:%M:%S")
        except ValueError:
            raise ValueError(f"Unsupported smart flag: {smart_flag}")

    # Interactive mode – ask the user for date and optional time
    while True:
        date_str = Prompt.ask(f"{prompt_msg} (YYYY-MM-DD or natural phrase like 'yesterday', '2 days ago')", default=default)
        if not date_str:
            # Empty input (user pressed Enter) – ask again
            console.print("[red]Date cannot be empty. Please provide a date in YYYY-MM-DD format or natural phrase.[/red]")
            continue
            
        try:
            dt = resolve_natural_date(date_str)
            return dt.strftime("%Y-%m-%d %H:%M:%S")
        except ValueError:
            pass # Not a natural phrase, try standard parsing
            
        try:
            _parse_date(date_str)
        except ValueError:
            console.print("[red]Invalid date format. Use YYYY-MM-DD or a natural phrase (e.g. 'yesterday').[/red]")
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
