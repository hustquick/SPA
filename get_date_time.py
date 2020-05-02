from datetime import datetime


def get_current_datetime():
    now = datetime.now()
    print("\n当前时间为:\n%s" % now)
    return now


if __name__ == '__main__':
    now_datetime = get_current_datetime()
