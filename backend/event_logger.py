from backend.analyzer import SessionAnalyzer
from backend.timeUtils import parse_timestamp

analyzer = SessionAnalyzer()

import win32evtlog
from datetime import datetime, timedelta


def get_logon_type(type_code):
    """Map logon type codes to descriptions."""
    logon_types = {
        '2': 'Interactive',
        '3': 'Network',
        '4': 'Batch',
        '5': 'Service',
        '7': 'Unlock',
        '8': 'NetworkCleartext',
        '9': 'NewCredentials',
        '10': 'RemoteInteractive',
        '11': 'CachedInteractive'
    }
    return logon_types.get(str(type_code), 'Unknown')


def get_session_logs(minutes_back=None, days_back=None):
    """
    Fetches and analyzes user session logs focusing on human interactions.

    Args:
        minutes_back (int, optional): Number of minutes to look back
        days_back (int, optional): Number of days to look back

    Returns:
        list: List of session log entries

    Note: If both parameters are provided, minutes_back takes precedence
    """
    try:
        hand = win32evtlog.OpenEventLog("localhost", "Security")
        flags = win32evtlog.EVENTLOG_BACKWARDS_READ | win32evtlog.EVENTLOG_SEQUENTIAL_READ

        session_logons = []
        session_logoffs = []

        # Calculate cutoff time based on provided parameters
        if minutes_back is not None:
            cutoff_time = datetime.now() - timedelta(minutes=minutes_back)
            time_window = f"last {minutes_back} minutes"
        elif days_back is not None:
            cutoff_time = datetime.now() - timedelta(days=days_back)
            time_window = f"last {days_back} days"
        else:
            cutoff_time = datetime.now() - timedelta(days=7)  # Default to 7 days
            time_window = "last 7 days"

        print(f"Fetching logs from {time_window}")
        print(f"Cutoff time: {cutoff_time}")

        while True:
            events = win32evtlog.ReadEventLog(hand, flags, 0)
            if not events:
                break

            for event in events:
                # Convert event time to standard format
                event_time = parse_timestamp(event.TimeGenerated)
                event_dt = datetime.strptime(event_time, '%Y-%m-%d %H:%M:%S')

                # Skip if event is older than cutoff
                if event_dt < cutoff_time:
                    break

                if event.EventID in [4624, 4634, 4625]:
                    data = event.StringInserts or []
                    # print(data)
                    log_entry = process_event(event, data, event_time)

                    if log_entry and log_entry['event_type'] == 'Logoff':
                        session_logoffs.append(log_entry)

                    elif log_entry and analyzer.is_human_session(log_entry):
                        analyzer.enrich_log_entry(log_entry)
                        session_logons.append(log_entry)

                        # Update session history for the user
                        analyzer.session_history[log_entry['user']].append(log_entry)

        win32evtlog.CloseEventLog(hand)

        # Sort logs by timestamp
        # session_logons.sort(key=lambda x: x['timestamp'])
        # session_logoffs.sort(key=lambda x: x['timestamp'])
        return session_logons, session_logoffs

    except Exception as e:
        print(f"Error fetching event logs: {e}")
        return []


def process_event(event, data, timestamp):
    """Process individual event and extract relevant information."""
    base_entry = {
        'timestamp': timestamp,
        'event_type': '',
        'user': '',
        'computer': '',
        'status': 'success',
        'logon_type': '',
        'source_ip': '',
        'process_name': '',
        'auth_package': '',
        'day_of_week': datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S').strftime('%A'),
        'hour_of_day': datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S').hour,
        'is_business_hours': analyzer.is_business_hours(timestamp),
        'risk_factors': []
    }

    try:
        if event.EventID == 4624:
            # Successful logon
            #print(f"Log ON data, length: {len(data)}")
            return process_logon(data, base_entry)
        elif event.EventID == 4634:  # Logoff
            #print(f'Logoff detected, length: {len(data)}')
            return process_logoff(data, base_entry)
        elif event.EventID == 4625:  # Failed logon
            return process_failed_logon(data, base_entry)
    except Exception as e:
        print(f"Error processing event {event.EventID}: {e}")
        return None

    return None


def process_logon(data, base_entry):
    """Process successful logon events."""
    if len(data) < 8:
        return None

    base_entry.update({
        'event_type': 'Logon',
        'user': data[5],
        'computer': data[1],
        'logon_type': get_logon_type(data[8]),
        'source_ip': data[18] if len(data) > 18 else '',
        'process_name': data[17] if len(data) > 17 else '',
        'auth_package': data[10] if len(data) > 10 else ''
    })
    return base_entry


def process_logoff(data, base_entry):
    """Process logoff events."""

    if len(data) < 3:
        return None

    base_entry.update({
        'event_type': 'Logoff',
        'user': data[1],
        'computer': data[2]
    })
    return base_entry


def process_failed_logon(data, base_entry):
    """Process failed logon events."""
    if len(data) < 8:
        return None

    base_entry.update({
        'event_type': 'Logon',
        'status': 'failed',
        'user': data[5],
        'computer': data[1],
        'logon_type': get_logon_type(data[8]),
        'source_ip': data[19] if len(data) > 19 else '',
        'failure_reason': data[7] if len(data) > 7 else '',
        'auth_package': data[10] if len(data) > 10 else ''
    })
    return base_entry
