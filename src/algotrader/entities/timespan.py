from enum import IntEnum, unique


@unique
class TimeSpan(IntEnum):
    Second = 1
    Minute = 60 * Second
    Hour = 60 * Minute
    Day = 24 * Hour
