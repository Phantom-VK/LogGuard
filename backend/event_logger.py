from backend.analyzer import SessionAnalyzer
from backend.event_processor import process_event
from backend.timeUtils import parse_timestamp
import win32evtlog
from datetime import datetime, timedelta

# Initialize the session analyzer
analyzer = SessionAnalyzer()


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
            cutoff_time = datetime.now() - timedelta(days=7)  # Default to 7 days

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
                    elif log_entry['status'] == 'failed':
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
