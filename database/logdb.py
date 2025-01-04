import sqlite3


def save_to_database(logs, db_name='event_logs.db'):
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
                subtype TEXT
            )
        """)

        # Insert logs into the table
        cursor.executemany("""
            INSERT INTO session_logs (timestamp, event_type, user, computer, status, subtype)
            VALUES (:timestamp, :event_type, :user, :computer, :status, :subtype)
        """, logs)

        # Commit changes and close the connection
        conn.commit()
        conn.close()

        print(f"Logs successfully saved to database: {db_name}")
    except Exception as e:
        print(f"Error saving logs to database: {e}")
