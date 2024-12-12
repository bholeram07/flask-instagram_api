from datetime import datetime
import pytz


def current_time_ist():
    ist = pytz.timezone('Asia/Kolkata')
    return datetime.now(ist)
