import pytz
from datetime import datetime, timedelta

def get_current_datetime(timedelta = timedelta(minutes=0)):
    current_time_ist = datetime.now(pytz.timezone("Asia/Kolkata"))
    # Convert to 12-hour format with full date and time
    formatted_time = (current_time_ist + timedelta).strftime("%Y-%m-%d %I:%M:%S %p")
    return formatted_time
