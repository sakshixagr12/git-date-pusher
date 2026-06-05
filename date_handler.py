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
    today = datetime.date.today()
    return _format_noon(today)


def get_valid_date(prompt_msg: str = "Enter date (YYYY-MM-DD, empty for today): ") -> str:
    """Prompt until a valid date string is supplied.

    Empty input returns today's date at noon.
    """
    while True:
        user_input = input(prompt_msg).strip()
        if not user_input:
            return get_today_str()
        try:
            parsed_date = datetime.datetime.strptime(user_input, "%Y-%m-%d").date()
            return _format_noon(parsed_date)
        except ValueError:
            print("❌ Invalid format. Please use YYYY-MM-DD (e.g., 2024-11-20).")


def generate_date_schedule(start: str, end: str, count: int) -> List[str]:
    """Generate an evenly spaced list of commit dates between *start* and *end*.

    Parameters
    ----------
    start : str
        Start date in ``YYYY-MM-DD`` format.
    end : str
        End date in ``YYYY-MM-DD`` format.
    count : int
        Number of dates to generate (typically the number of files).

    Returns
    -------
    List[str]
        List of date strings formatted as ``YYYY-MM-DD 12:00:00``.

    The first date is *start* and the last is *end*; intermediate dates are
    calculated by linear interpolation of days.
    """
    if count < 1:
        raise ValueError("Count must be at least 1")
    try:
        start_dt = datetime.datetime.strptime(start, "%Y-%m-%d")
        end_dt = datetime.datetime.strptime(end, "%Y-%m-%d")
    except ValueError as exc:
        raise ValueError("Start and end dates must be in YYYY-MM-DD format") from exc
    if end_dt < start_dt:
        raise ValueError("End date must be on or after start date")

    total_days = (end_dt - start_dt).days
    if count == 1:
        # Only one file – use start date
        return [_format_noon(start_dt.date())]

    # Compute step as a float to distribute evenly, then round each day offset
    step = total_days / (count - 1)
    schedule = []
    for i in range(count):
        delta = round(step * i)
        cur_date = (start_dt + datetime.timedelta(days=delta)).date()
        schedule.append(_format_noon(cur_date))
    return schedule
