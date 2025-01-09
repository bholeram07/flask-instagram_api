from datetime import datetime
import pytz


def current_time_ist()->str:
    ist = pytz.timezone('Asia/Kolkata')
    return datetime.now(ist)
