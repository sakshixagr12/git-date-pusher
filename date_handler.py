# Pure core date handling (no UI)
import datetime
from typing import List


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
