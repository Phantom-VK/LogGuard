import json
from collections import defaultdict
from datetime import datetime


class SessionAnalyzer:
    def __init__(self):
        self.session_history = defaultdict(list)
        self.suspicious_ips = set()
        self.known_workstations = set()

    @staticmethod
    def is_human_session(log_entry):
        """
        Determine if the session is from a human user rather than a system account.
        """
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
        """Add additional security-relevant features for anomaly detection."""
        user = log_entry['user']
        computer = log_entry['computer']
        source_ip = log_entry.get('source_ip', '')

        # Track known workstations
        if computer:
            self._update_workstation_history(computer=computer)

        # Add risk factors
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

        # Add user behavior analysis
        if user in self.session_history:
            if self._is_concurrent_login(log_entry):
                risk_factors.append('concurrent_login')
            if self._is_rapid_login(log_entry):
                risk_factors.append('rapid_login_attempts')

        log_entry['risk_factors'] = risk_factors
        log_entry['risk_score'] = len(risk_factors)

    @staticmethod
    def is_business_hours(timestamp):
        """Check if the timestamp is within business hours (9 AM - 6 PM, Monday-Friday)."""
        dt = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')
        return (
                dt.weekday() < 5 and  # Monday-Friday
                9 <= dt.hour < 18  # 9 AM - 6 PM
        )

    @staticmethod
    def _is_internal_ip(ip):
        """Check if IP address is internal."""
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
        """Update known workstations set."""
        self.known_workstations.add(computer)

    def _is_concurrent_login(self, log_entry):
        """Check for concurrent logins from different locations."""
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
        """Check for unusually rapid login attempts."""
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


