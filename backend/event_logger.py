from backend.analyzer import SessionAnalyzer
from backend.timeUtils import parse_timestamp
import win32evtlog
from datetime import datetime, timedelta

# Initialize the session analyzer
analyzer = SessionAnalyzer()

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
        tuple: Two lists containing session logons and logoffs
    """
    try:
        hand = win32evtlog.OpenEventLog("localhost", "Security")
        flags = win32evtlog.EVENTLOG_BACKWARDS_READ | win32evtlog.EVENTLOG_SEQUENTIAL_READ

        session_logons = []
        session_logoffs = []

        # Calculate cutoff time based on parameters
        if minutes_back is not None:
            cutoff_time = datetime.now() - timedelta(minutes=minutes_back)
        elif days_back is not None:
            cutoff_time = datetime.now() - timedelta(days=days_back)
        else:
            cutoff_time = datetime.now() - timedelta(days=100)  # Default to 7 days

        while True:
            events = win32evtlog.ReadEventLog(hand, flags, 0)
            if not events:
                break

            for event in events:
                event_time = parse_timestamp(event.TimeGenerated)
                event_dt = datetime.strptime(event_time, '%Y-%m-%d %H:%M:%S')

                # Skip if event is older than cutoff
                if event_dt < cutoff_time:
                    continue

                if event.EventID in [4624, 4634, 4625]:
                    data = event.StringInserts or []
                    log_entry = process_event(event, data, event_time)

                    if log_entry and log_entry['event_type'] == 'Logoff':
                        session_logoffs.append(log_entry)
                    elif log_entry['status'] =='failed':
                        session_logons.append(log_entry)
                        # print(f"Processing Event ID: {event.EventID}, Status: {log_entry['status']}")
                    elif log_entry and analyzer.is_human_session(log_entry):
                        log_entry = assess_risk(log_entry)
                        session_logons.append(log_entry)
                        analyzer.session_history[log_entry['user']].append(log_entry)

        win32evtlog.CloseEventLog(hand)

        return session_logons, session_logoffs

    except Exception as e:
        print(f"Error fetching event logs: {e}")
        return [], []

def process_event(event, data, timestamp):
    """Process individual event and extract relevant information."""
    base_entry = {
        'timestamp': timestamp,
        'event_type': '',
        'user': '',
        'domain': '',
        'user_sid': '',
        'account_type': '',
        'logon_id': '',
        'session_duration': 0,
        'status': 'success',
        'logon_type': '',
        'source_ip': '',
        'destination_ip': '',
        'workstation_name': '',
        'failure_reason': '',
        'elevated_token': False,
        'process_name': '',
        'auth_package': '',
        'risk_factors': [],
        'risk_score': 0,
        'authentication_method': '',
        'day_of_week': datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S').strftime('%A'),
        'hour_of_day': datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S').hour,
        'is_business_hours': analyzer.is_business_hours(timestamp),
        'event_id': event.EventID,
        'event_task_category': event.EventCategory,
        'target_user_name': '',
        'caller_process_name': ''
    }

    try:
        if event.EventID == 4624:  # Successful logon
            return process_logon(data, base_entry)
        elif event.EventID == 4634:  # Logoff
            return process_logoff(data, base_entry)
        elif event.EventID == 4625:  # Failed logon
            return process_failed_logon(data, base_entry)
    except Exception as e:
        print(f"Error processing event {event.EventID}: {e}")
    return None

def process_logon(data, base_entry):
    """Process successful logon events."""
    if len(data) < 10:
        return None

    base_entry.update({
        'event_type': 'Logon',
        'user': data[5],
        'domain': data[6],
        'user_sid': data[4],
        'logon_id': data[3],
        'logon_type': get_logon_type(data[8]),
        'source_ip': data[18] if len(data) > 18 else '',
        'workstation_name': data[1],
        'process_name': data[17] if len(data) > 17 else '',
        'auth_package': data[10] if len(data) > 10 else '',
        'elevated_token': 'Yes' in data[20] if len(data) > 20 else False,
        'authentication_method': data[11] if len(data) > 11 else ''
    })
    return base_entry


def process_logoff(data, base_entry):
    """Process logoff events."""
    if len(data) < 3:
        return None

    logon_id = data[3]
    logoff_time = base_entry.get('timestamp')  # Assuming timestamp is stored in the base_entry
    logon_time = analyzer.get_logon_time(logon_id)  # Implement this function to retrieve the logon time

    session_duration = None
    if logon_time and logoff_time:
        session_duration = analyzer.get_session_duration(logon_time, logoff_time)

    base_entry.update({
        'event_type': 'Logoff',
        'user': data[1],
        'domain': data[2],
        'logon_id': logon_id,
        'session_duration': session_duration
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
        'domain': data[6],
        'user_sid': data[4],
        'logon_id': data[3],
        'logon_type': get_logon_type(data[8]),
        'source_ip': data[19] if len(data) > 19 else '',
        'failure_reason': data[7] if len(data) > 7 else '',
        'auth_package': data[10] if len(data) > 10 else ''
    })
    return base_entry

def assess_risk(log_entry):
    """Assess risk score and factors for a session."""
    risk_score = 0
    risk_factors = []

    if log_entry['logon_type'] == 'RemoteInteractive':
        risk_score += 20
        risk_factors.append("Remote Interactive Logon")
    if not log_entry['source_ip']:
        risk_score += 10
        risk_factors.append("Missing Source IP")
    if log_entry['elevated_token']:
        risk_score += 30
        risk_factors.append("Elevated Token")

    log_entry['risk_score'] = risk_score
    log_entry['risk_factors'] = risk_factors
    return log_entry
