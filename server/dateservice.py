from datetime import datetime
from zoneinfo import ZoneInfo

def get_current_date():
    """Returns the current date and time in ISO format with timezone info."""
    now = datetime.now(ZoneInfo("America/New_York"))
    return now.strftime("%A, %B %d, %Y %I:%M %p %Z")  # for the prompt
    