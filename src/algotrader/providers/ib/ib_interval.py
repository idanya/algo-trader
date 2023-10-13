from datetime import datetime

from algotrader.entities.timespan import TimeSpan


def datetime_to_api_string(d: datetime) -> str:
    return d.strftime("%Y%m%d %H:%M:%S")


def timespan_to_api_str(timespan: TimeSpan) -> str:
    if timespan == TimeSpan.Day:
        return "1 day"
    elif timespan == TimeSpan.Minute:
        return "1 min"
    else:
        raise Exception("data provider does not support this timespan")
