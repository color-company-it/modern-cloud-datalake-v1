"""
Here are some common date formats that you might encounter in a relational database:

YYYY-MM-DD (ISO 8601 format)
MM/DD/YYYY
DD/MM/YYYY
YYYY-MM-DDTHH:MM:SS (ISO 8601 extended format)
YYYY-MM-DD HH:MM:SS (24-hour time format)
YYYY-MM-DD hh:MM:SS (12-hour time format)
YYYY-MM-DD HH:MM:SS.sss (millisecond precision)
YYYY-MM-DD HH:MM:SS.ssssss (microsecond precision)
YYYY-MM-DD HH:MM:SS.sssssssss (nanosecond precision)
YYYY-MM-DDTHH:MM:SS.sssZ (ISO 8601 extended format with time zone)
YYYY-MM-DDTHH:MM:SS.ssssssZ (ISO 8601 extended format with time zone and microsecond precision)
YYYY-MM-DDTHH:MM:SS.sssssssssZ (ISO 8601 extended format with time zone and nanosecond precision)
YYYY-MM-DDTHH:MM:SS+HH:MM (ISO 8601 extended format with time zone offset)
YYYY-MM-DDTHH:MM:SS.sss+HH:MM (ISO 8601 extended format with time zone offset and millisecond precision)
YYYY-MM-DDTHH:MM:SS.ssssss+HH:MM (ISO 8601 extended format with time zone offset and microsecond precision)
YYYY-MM-DDTHH:MM:SS.sssssssss+HH:MM (ISO 8601 extended format with time zone offset and nanosecond precision)
"""

DATETIME_FMTS: dict = {
    "%Y-%m-%d": "ISO_LOCAL_DATE",
    "%Y-%m-%d %H:%M:%S": "ISO_LOCAL_DATETIME",
    "%Y-%m-%dT%H:%M:%S": "ISO_OFFSET_DATETIME",
    "%a %b %d %H:%M:%S %Y": "RFC_822",
    "%a, %d %b %Y %H:%M:%S %Z": "RFC_1123",
}

DATETIME_FMTS_REGEX: dict = {
    "%Y-%m-%d": r"\d{4}-\d{2}-\d{2}",
    "%Y-%m-%d %H:%M:%S": r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}",
    "%Y-%m-%dT%H:%M:%S": r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}",
    "%a %b %d %H:%M:%S %Y": r"[A-Z][a-z]{2} [A-Z][a-z]{2} \d{2} \d{2}:\d{2}:\d{2} \d{4}",
    "%a, %d %b %Y %H:%M:%S %Z": r"[A-Z][a-z]{2}, \d{2} [A-Z][a-z]{2} \d{4} \d{2}:\d{2}:\d{2} [A-Z]{3}",
}
