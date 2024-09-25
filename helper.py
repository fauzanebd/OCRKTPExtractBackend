import datetime
import re


def extract_date(date_text):
    try:
        match = re.search(r"(\d{1,2})([-/\.])(\d{2})\2(\d{4})", date_text)
        if match:
            day, month, year = int(match.group(1)), int(match.group(3)), int(match.group(4))
            return datetime.datetime(year, month, day)
        parsed_date = datetime.datetime.strptime(date_text, "%Y %m-%d")
        return parsed_date
    except ValueError:
        pass

    try:
        parsed_date = datetime.datetime.strptime(date_text, "%d%m %Y")
        return parsed_date
    except ValueError:
        pass

    try:
        parsed_date = datetime.datetime.strptime(date_text, "%d %m-%Y")
        return parsed_date
    except ValueError:
        pass

    date_pattern = r"(\d{1,4})(?:[-/\.])(\d{1,2})(?:[-/\.])(\d{2,4})"
    match = re.search(date_pattern, date_text)
    if match:
        day, month, year = map(lambda x: int(x) if 1 <= int(x) <= 31 else None, match.groups())
        if day is not None and month is not None and year is not None:
            try:
                return datetime.datetime(year, month, day)
            except ValueError:
                return None
    return None