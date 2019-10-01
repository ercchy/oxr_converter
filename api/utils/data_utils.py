from datetime import datetime

"""
Converts datetime object to string

Needed for serialization
"""
def datetime_converter(o):
    if isinstance(o, datetime):
        return o.__str__()