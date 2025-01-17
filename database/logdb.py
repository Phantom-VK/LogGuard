import sqlite3
import json


def save_to_database(logs, db_name):
    """
    Save logs to an SQLite database.
    """
    try:
        # Connect to SQLite database
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()

        # Create table if not exists
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS session_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                event_type TEXT,
                user TEXT,
                computer TEXT,
                status TEXT,
                logon_type TEXT,
                source_ip TEXT,
                process_name TEXT,
                auth_package TEXT,
                day_of_week TEXT,
                hour_of_day INTEGER,
                is_business_hours BOOLEAN,
                risk_factors TEXT
                
            )
        """)

        # Prepare logs for insertion
        formatted_logs = []
        for log in logs:
            formatted_logs.append({
                'timestamp': log.get('timestamp', ''),
                'event_type': log.get('event_type', ''),
                'user': log.get('user', ''),
                'computer': log.get('computer', ''),
                'status': log.get('status', ''),
                'logon_type': log.get('logon_type', ''),
                'source_ip': log.get('source_ip', ''),
                'process_name': log.get('process_name', ''),
                'auth_package': log.get('auth_package', ''),
                'day_of_week': log.get('day_of_week', ''),
                'hour_of_day': log.get('hour_of_day', 0),
                'is_business_hours': log.get('is_business_hours', False),
                'risk_factors': json.dumps(log.get('risk_factors', []))  # Store as JSON string
            })

        # Insert logs into the table
        cursor.executemany("""
            INSERT INTO session_logs (
                timestamp, event_type, user, computer, status, logon_type,
                source_ip, process_name, auth_package, day_of_week, hour_of_day,
                is_business_hours, risk_factors
            )
            VALUES (
                :timestamp, :event_type, :user, :computer, :status, :logon_type,
                :source_ip, :process_name, :auth_package, :day_of_week, :hour_of_day,
                :is_business_hours, :risk_factors
            )
        """, formatted_logs)

        # Commit changes and close the connection
        conn.commit()
        conn.close()

        print(f"Logs successfully saved to database: {db_name}")
    except Exception as e:
        print(f"Error saving logs to database: {e}")
