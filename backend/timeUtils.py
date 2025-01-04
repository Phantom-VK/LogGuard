from datetime import datetime


def parse_timestamp(time_str):
    """Parse different timestamp formats and return standardized datetime string"""
    try:
        formats = [
            '%Y-%m-%d %H:%M:%S',
            '%a %b %d %H:%M:%S %Y',  # Sat Jan 4 16:49:15 2025
            '%m/%d/%Y %H:%M:%S'
        ]

        # If time_str is already a datetime object
        if isinstance(time_str, datetime):
            return time_str.strftime('%Y-%m-%d %H:%M:%S')

        # Try each format
        for fmt in formats:
            try:
                return datetime.strptime(time_str, fmt).strftime('%Y-%m-%d %H:%M:%S')
            except ValueError:
                continue

        # Try parsing with datetime object
        return datetime.strptime(str(time_str), '%c').strftime('%Y-%m-%d %H:%M:%S')

    except Exception as e:
        print(f"Error parsing timestamp {time_str}: {e}")
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S')