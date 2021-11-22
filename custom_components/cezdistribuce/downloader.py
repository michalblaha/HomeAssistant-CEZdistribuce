import requests
import datetime

try:
    # python 3.9+
    from zoneinfo import ZoneInfo
except ImportError:
    # python 3.6-3.8
    from backports.zoneinfo import ZoneInfo


BASE_URL = "https://www.cezdistribuce.cz/distHdo/adam/containers/"
CEZ_TIMEZONE = ZoneInfo("Europe/Prague")


def getCorrectRegionName(region):
    region = region.lower()
    for x in ["zapad", "sever", "stred", "vychod", "morava"]:
        if x in region:
            return x


def getRequestUrl(region, code):
    region = getCorrectRegionName(region)
    return BASE_URL + region + "?&code=" + code.upper()


def timeInRange(start, end, x):
    if start <= end:
        return start <= x <= end
    else:
        return start <= x or x <= end


def parseTime(date_time_str):
    if not date_time_str:
        return datetime.time(0, 0)
    else:
        return datetime.datetime.strptime(date_time_str, "%H:%M").time()


def parseDate(date_time_str):
    return datetime.datetime.strptime(date_time_str, "%Y-%m-%d %H:%M:%S.%f")


def isHdo(jsonCalendar, daytime=datetime.datetime.utcnow()):
    """
    Find out if the HDO is enabled for the current timestamp

    :param jsonCalendar: JSON with calendar schedule from CEZ
    :param daytime: relevant time in UTC to check if HDO is on or not
    :return: bool
    """
    # convert daytime to timezone CEZ is using on website
    daytime.replace(tzinfo=ZoneInfo("UTC"))
    daytime = daytime.astimezone(CEZ_TIMEZONE)
    daytime.replace(tzinfo=None)

    # select Mon-Fri schedule or Sat-Sun schedule according to current date
    if daytime.weekday() < 5:
        dayCalendar = jsonCalendar[0]
    else:
        dayCalendar = jsonCalendar[1]

    checkedTime = daytime.time()
    hdo = False

    # iterate over scheduled times in calendar schedule
    for i in range(1, 11):
        startTime = parseTime(dayCalendar["CAS_ZAP_" + str(i)])
        endTime = parseTime(dayCalendar["CAS_VYP_" + str(i)])
        hdo = hdo or timeInRange(start=startTime, end=endTime, x=checkedTime)
    return hdo
