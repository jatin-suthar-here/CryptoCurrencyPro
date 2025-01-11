from datetime import datetime
from zoneinfo import ZoneInfo


def get_current_time():
    # Get the current UTC time
    current_utc = datetime.now(tz=ZoneInfo("UTC"))

    # Convert to Indian Standard Time (IST)
    current_ist = current_utc.astimezone(ZoneInfo("Asia/Kolkata"))

    # Print the IST date and time
    print("Current date and time in IST:", current_ist)

    # Optional: Format the IST datetime
    formatted_ist = current_ist.strftime("%Y-%m-%d %H:%M:%S")
    return formatted_ist