from datetime import datetime
import re

default_date_format = "%Y-%m-%d"
default_time_format = "%H:%M:%S"
default_datetime_format = f"{default_date_format}, {default_time_format}"

def safe_date(date: str) -> datetime.date:
    try:
        return datetime.strptime(date, default_datetime_format).date()
    except ValueError as e:
        try:
            return datetime.strptime(date, default_date_format).date()
        except ValueError as e:
            print(e)
            return None

def extract_first_date(text: str) -> datetime.date:
    '''
    Extract first date found in text using regex

    :param text: text inclusing a date in the format YYYY-MM-DD
    :return: datetime.date
    '''
    match = re.search(r'\d{4}-\d{2}-\d{2}', text)
    return datetime.strptime(match.group(), '%Y-%m-%d').date()