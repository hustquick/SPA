from datetime import datetime
from dateutil.parser import parse

def get_current_datetime():
    now = datetime.now()
    print("Current time is:\n%s"%now)
    return now

if __name__ == '__main__':
    now = get_current_datetime()

