import sqlite3
import json


def save_to_database(logs, db_name):
    """
    Save logs to an SQLite database, ensuring no duplicate rows are inserted.
    """
    try:
        # Connect to SQLite database
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()

        # Create table if not exists
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS session_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                logon_type TEXT,
                timestamp TEXT UNIQUE,  -- Ensures timestamp is unique for duplicate prevention
                day_of_week TEXT,
                hour_of_day INTEGER,
                is_business_hours BOOLEAN,
                user TEXT,
                domain TEXT,
                user_sid TEXT,
                account_type TEXT,
                event_type TEXT,
                logon_id TEXT,
                session_duration REAL,
                source_ip TEXT,
                destination_ip TEXT,
                workstation_name TEXT,
                status TEXT,
                failure_reason TEXT,
                elevated_token BOOLEAN,
                risk_factors TEXT,
                risk_score REAL,
                authentication_method TEXT,
                event_id INTEGER,
                event_task_category TEXT,
                target_user_name TEXT,
                caller_process_name TEXT
            )
        """)

        # Prepare logs for insertion
        formatted_logs = []
        for log in logs:
            formatted_logs.append({
                'logon_type': log.get('logon_type', ''),
                'timestamp': log.get('timestamp', ''),  # Use this as a unique field
                'day_of_week': log.get('day_of_week', ''),
                'hour_of_day': log.get('hour_of_day', 0),
                'is_business_hours': log.get('is_business_hours', False),
                'user': log.get('user', ''),
                'domain': log.get('domain', ''),
                'user_sid': log.get('user_sid', ''),
                'account_type': log.get('account_type', ''),
                'event_type': log.get('event_type', ''),
                'logon_id': log.get('logon_id', ''),
                'session_duration': log.get('session_duration', 0.0),
                'source_ip': log.get('source_ip', ''),
                'destination_ip': log.get('destination_ip', ''),
                'workstation_name': log.get('workstation_name', ''),
                'status': log.get('status', ''),
                'failure_reason': log.get('failure_reason', ''),
                'elevated_token': log.get('elevated_token', False),
                'risk_factors': json.dumps(log.get('risk_factors', [])),  # Store as JSON string
                'risk_score': log.get('risk_score', 0.0),
                'authentication_method': log.get('authentication_method', ''),
                'event_id': log.get('event_id', 0),
                'event_task_category': log.get('event_task_category', ''),
                'target_user_name': log.get('target_user_name', ''),
                'caller_process_name': log.get('caller_process_name', '')
            })

        # Insert logs into the table using INSERT OR IGNORE
        cursor.executemany("""
            INSERT OR IGNORE INTO session_logs (
                logon_type, timestamp, day_of_week, hour_of_day, is_business_hours, user,
                domain, user_sid, account_type, event_type, logon_id, session_duration,
                source_ip, destination_ip, workstation_name, status, failure_reason,
                elevated_token, risk_factors, risk_score, authentication_method,
                event_id, event_task_category, target_user_name, caller_process_name
            )
            VALUES (
                :logon_type, :timestamp, :day_of_week, :hour_of_day, :is_business_hours, :user,
                :domain, :user_sid, :account_type, :event_type, :logon_id, :session_duration,
                :source_ip, :destination_ip, :workstation_name, :status, :failure_reason,
                :elevated_token, :risk_factors, :risk_score, :authentication_method,
                :event_id, :event_task_category, :target_user_name, :caller_process_name
            )
        """, formatted_logs)

        # Commit changes and close the connection
        conn.commit()
        conn.close()

        print(f"Logs successfully saved to database: {db_name}")
    except Exception as e:
        print(f"Error saving logs to database: {e}")
