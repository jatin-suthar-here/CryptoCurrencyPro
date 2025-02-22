import pytz
from datetime import datetime, timedelta

# def get_current_datetime(timedelta = timedelta(minutes=0)):
#     current_time_ist = datetime.now(pytz.timezone("Asia/Kolkata"))
#     # Convert to 12-hour format with full date and time
#     formatted_time = (current_time_ist + timedelta).strftime("%Y-%m-%d %I:%M:%S %p")
#     return formatted_time


from datetime import datetime
import pytz

def get_current_datetime(timedelta = timedelta(minutes=0)):
    # Define the timezone for India
    india_timezone = pytz.timezone('Asia/Kolkata')
    
    # Get the current time in India's timezone
    india_time = datetime.now(india_timezone) + timedelta
    
    # Format the time in 12-hour format with AM/PM
    formatted_time = india_time.strftime('%Y-%m-%d %I:%M:%S %p')
    
    return formatted_time


print(get_current_datetime())
print(get_current_datetime(timedelta=timedelta(minutes=120)))