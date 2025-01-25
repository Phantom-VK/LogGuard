import json
from collections import defaultdict
from datetime import datetime
import logging


class SessionAnalyzer:
    def __init__(self, business_hours=(9, 18)):
        """
        Initialize the SessionAnalyzer.
        :param business_hours: Tuple defining the start and end of business hours (24-hour format).
        """
        self.session_history = defaultdict(list)
        self.suspicious_ips = set()
        self.known_workstations = set()
        self.logon_sessions = {}
        self.business_hours = business_hours
        self.RISK_WEIGHTS = {
            'suspicious_ip': 3,
            'external_ip': 2,
            'new_workstation': 1,
            'outside_business_hours': 1,
            'concurrent_login': 2,
            'rapid_login_attempts': 2,
        }
        # Configure logging
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

    def get_logon_time(self, logon_id):
        """Retrieve the logon time for a given logon_id."""
        return self.logon_sessions.get(logon_id)

    def record_logon_event(self, logon_id, logon_time):
        """Record a logon event for tracking."""
        self.logon_sessions[logon_id] = logon_time

    @staticmethod
    def is_human_session(log_entry):
        """
        Determine if a log entry represents a human session.
        :param log_entry: Dictionary containing log details.
        :return: True if the session is human, False otherwise.
        """
        system_accounts = {'SYSTEM', 'LOCAL SERVICE', 'NETWORK SERVICE', 'ANONYMOUS LOGON'}
        system_prefixes = ('$', 'NT ', 'UMFD-', 'DWM-', 'WINDOW MANAGER')
        user = log_entry.get('user', '').upper()
        logon_type = log_entry.get('logon_type', '')
        return (
            user
            and user not in system_accounts
            and not user.startswith(system_prefixes)
            and logon_type in {'Interactive', 'RemoteInteractive', 'CachedInteractive', 'Unlock'}
        )

    def enrich_log_entry(self, log_entry):
        """
        Analyze and enrich a log entry with risk factors and a risk score.
        :param log_entry: Dictionary containing log details.
        """
        # Validate input
        if not isinstance(log_entry, dict) or 'timestamp' not in log_entry:
            raise ValueError("Invalid log entry format")

        user = log_entry.get('user')
        computer = log_entry.get('computer')
        source_ip = log_entry.get('source_ip', '')
        timestamp = log_entry.get('timestamp')

        # Update workstation history
        if computer:
            self._update_workstation_history(computer)

        risk_factors = []

        # Analyze risk factors
        if source_ip and source_ip not in {'127.0.0.1', '::1', '-'}:
            if source_ip in self.suspicious_ips:
                risk_factors.append('suspicious_ip')
            if not self._is_internal_ip(source_ip):
                risk_factors.append('external_ip')

        if computer and computer not in self.known_workstations:
            risk_factors.append('new_workstation')

        if not self.is_business_hours(timestamp):
            risk_factors.append('outside_business_hours')

        if user in self.session_history:
            if self._is_concurrent_login(log_entry):
                risk_factors.append('concurrent_login')
            if self._is_rapid_login(log_entry):
                risk_factors.append('rapid_login_attempts')

        # Calculate risk score
        log_entry['risk_factors'] = risk_factors
        log_entry['risk_score'] = sum(self.RISK_WEIGHTS[risk] for risk in risk_factors)

    def is_business_hours(self, timestamp):
        """
        Check if the given timestamp falls within business hours.
        :param timestamp: String representation of the timestamp.
        :return: True if within business hours, False otherwise.
        """
        try:
            dt = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')
            return (
                dt.weekday() < 5  # Monday-Friday
                and self.business_hours[0] <= dt.hour < self.business_hours[1]
            )
        except ValueError:
            logging.warning(f"Invalid timestamp format: {timestamp}")
            return False

    @staticmethod
    def _is_internal_ip(ip):
        """
        Check if an IP address is internal.
        :param ip: String representation of the IP address.
        :return: True if internal, False otherwise.
        """
        if ip in {'-', '::1', '127.0.0.1'}:
            return True
        return ip.startswith(('10.', '172.16.', '192.168.'))

    def _update_workstation_history(self, computer):
        """Update the known workstation history."""
        self.known_workstations.add(computer)

    def _is_concurrent_login(self, log_entry):
        """Check for concurrent logins from different workstations."""
        if log_entry['event_type'] != 'Logon':
            return False
        recent_logins = [
            entry for entry in self.session_history[log_entry['user']]
            if (
                entry['event_type'] == 'Logon'
                and entry['status'] == 'success'
                and entry['computer'] != log_entry['computer']
                and abs(
                    (datetime.strptime(entry['timestamp'], '%Y-%m-%d %H:%M:%S')
                     - datetime.strptime(log_entry['timestamp'], '%Y-%m-%d %H:%M:%S')).total_seconds()
                ) < 300
            )
        ]
        return bool(recent_logins)

    def _is_rapid_login(self, log_entry):
        """Check for rapid login attempts within 1 minute."""
        if log_entry['event_type'] != 'Logon':
            return False
        recent_attempts = [
            entry for entry in self.session_history[log_entry['user']]
            if abs(
                (datetime.strptime(entry['timestamp'], '%Y-%m-%d %H:%M:%S')
                 - datetime.strptime(log_entry['timestamp'], '%Y-%m-%d %H:%M:%S')).total_seconds()
            ) < 60
        ]
        return len(recent_attempts) >= 3

    def get_session_duration(self, logon_time, logoff_time):
        """Calculate the duration of a session."""
        try:
            logon_dt = datetime.strptime(logon_time, '%Y-%m-%d %H:%M:%S')
            logoff_dt = datetime.strptime(logoff_time, '%Y-%m-%d %H:%M:%S')
            return (logoff_dt - logon_dt).total_seconds()
        except ValueError as e:
            logging.error(f"Error parsing timestamps: {e}")
            return None


def save_to_json(logs, filename):
    """Save logs to JSON format."""
    try:
        with open(filename, 'w') as f:
            json.dump(logs, f, indent=2)
        logging.info(f"Logs saved to {filename}")
    except Exception as e:
        logging.error(f"Failed to save logs: {e}")
