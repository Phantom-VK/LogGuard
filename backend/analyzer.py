import json
from collections import defaultdict
from datetime import datetime


class SessionAnalyzer:
    def __init__(self):
        self.session_history = defaultdict(list)
        self.suspicious_ips = set()
        self.known_workstations = set()
        self.logon_sessions = {}

    def get_logon_time(self, logon_id):
        """Retrieve the logon time for a given logon_id."""
        return self.logon_sessions.get(logon_id)

    def record_logon_event(self, logon_id, logon_time):
        """Record a logon event for tracking."""
        self.logon_sessions[logon_id] = logon_time

    @staticmethod
    def is_human_session(log_entry):
        system_accounts = {'SYSTEM', 'LOCAL SERVICE', 'NETWORK SERVICE', 'ANONYMOUS LOGON'}
        system_prefixes = ('$', 'NT ', 'UMFD-', 'DWM-', 'WINDOW MANAGER')
        user = log_entry.get('user', '').upper()
        logon_type = log_entry.get('logon_type', '')
        return (
                user and
                user not in system_accounts and
                not user.startswith(system_prefixes) and
                logon_type in {'Interactive', 'RemoteInteractive', 'CachedInteractive', 'Unlock'}
        )

    def enrich_log_entry(self, log_entry):
        user = log_entry['user']
        computer = log_entry['computer']
        source_ip = log_entry.get('source_ip', '')
        if computer:
            self._update_workstation_history(computer=computer)
        risk_factors = []
        if source_ip and source_ip not in {'127.0.0.1', '::1', '-'}:
            if source_ip in self.suspicious_ips:
                risk_factors.append('suspicious_ip')
            if not self._is_internal_ip(source_ip):
                risk_factors.append('external_ip')
        if computer and computer not in self.known_workstations:
            risk_factors.append('new_workstation')
        if not self.is_business_hours(log_entry['timestamp']):
            risk_factors.append('outside_business_hours')
        if user in self.session_history:
            if self._is_concurrent_login(log_entry):
                risk_factors.append('concurrent_login')
            if self._is_rapid_login(log_entry):
                risk_factors.append('rapid_login_attempts')
        log_entry['risk_factors'] = risk_factors
        log_entry['risk_score'] = len(risk_factors)

    @staticmethod
    def is_business_hours(timestamp):
        dt = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')
        return (
                dt.weekday() < 5 and  # Monday-Friday
                9 <= dt.hour < 18  # 9 AM - 6 PM
        )

    @staticmethod
    def _is_internal_ip(ip):
        if ip in {'-', '::1', '127.0.0.1'}:
            return True
        try:
            return (
                    ip.startswith('10.') or
                    ip.startswith('172.16.') or
                    ip.startswith('192.168.')
            )
        except:
            return False

    def _update_workstation_history(self, computer):
        self.known_workstations.add(computer)

    def _is_concurrent_login(self, log_entry):
        if log_entry['event_type'] != 'Logon':
            return False
        recent_logins = [
            entry for entry in self.session_history[log_entry['user']]
            if (
                    entry['event_type'] == 'Logon' and
                    entry['status'] == 'success' and
                    entry['computer'] != log_entry['computer'] and
                    abs(datetime.strptime(entry['timestamp'], '%Y-%m-%d %H:%M:%S') -
                        datetime.strptime(log_entry['timestamp'], '%Y-%m-%d %H:%M:%S')).total_seconds() < 300
            )
        ]
        return len(recent_logins) > 0

    def _is_rapid_login(self, log_entry):
        if log_entry['event_type'] != 'Logon':
            return False
        recent_attempts = [
            entry for entry in self.session_history[log_entry['user']]
            if (
                    entry['event_type'] == 'Logon' and
                    abs(datetime.strptime(entry['timestamp'], '%Y-%m-%d %H:%M:%S') -
                        datetime.strptime(log_entry['timestamp'], '%Y-%m-%d %H:%M:%S')).total_seconds() < 60
            )
        ]
        return len(recent_attempts) >= 3

    def get_session_duration(self, logon_time, logoff_time):
        try:
            logon_dt = datetime.strptime(logon_time, '%Y-%m-%d %H:%M:%S')
            logoff_dt = datetime.strptime(logoff_time, '%Y-%m-%d %H:%M:%S')
            return (logoff_dt - logon_dt).total_seconds()
        except ValueError as e:
            print(f"Error parsing timestamps: {e}")
            return None


def save_to_json(logs, filename):
    """Save logs to JSON format."""
    with open(filename, 'w') as f:
        json.dump(logs, f, indent=2)


# # Add a debug print function to help troubleshoot
# def print_event_details(event):
#     """Debug function to print raw event details"""
#     print("\nEvent Details:")
#     print(f"EventID: {event.EventID}")
#     print(f"TimeGenerated: {event.TimeGenerated}")
#     print(f"StringInserts: {event.StringInserts if event.StringInserts else 'None'}")


