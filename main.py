import time
from collections import defaultdict
from datetime import datetime
import os
import sys

from backend.analyzer import save_to_json
from database.toCSV import query_database, save_to_csv
from backend.event_logger import get_session_logs
from database.logdb import save_to_database

def get_base_path():
    # Check if the script is running as a packaged .exe
    if getattr(sys, 'frozen', False):
        # If frozen (i.e., .exe), use sys._MEIPASS which is the temp directory PyInstaller uses
        return sys._MEIPASS
    return os.path.dirname(os.path.abspath(__file__))  # Use current script directory

if __name__ == '__main__':
    base_path = get_base_path()  # Get the base path

    # Example usage with minutes
    print("Analyzing recent login activity...")
    start_time = time.time()
    logons, logoffs = get_session_logs(days_back=10)
    print(f"\nFound {len(logons)} human user sessions")

    # Show time range of logs
    if logons:
        first_log = datetime.strptime(logons[0]['timestamp'], '%Y-%m-%d %H:%M:%S')
        last_log = datetime.strptime(logons[-1]['timestamp'], '%Y-%m-%d %H:%M:%S')
        print(f"Time range: {first_log} to {last_log}")

    # Group by risk score
    risk_groups = defaultdict(list)
    for log in logons:
        risk_groups[log.get('risk_score', 0)].append(log)

    print("\nRisk Score Distribution:")
    for score in sorted(risk_groups.keys()):
        print(f"Risk Score {score}: {len(risk_groups[score])} events")

    # Save logs with timestamp in filename, using base path
    output_file = os.path.join(base_path, 'session_logons.json')
    output_file2 = os.path.join(base_path, 'session_logoffs.json')
    save_to_json(logons, filename=output_file)
    save_to_json(logoffs, filename=output_file2)

    # Save to databases and CSV
    save_to_database(logs=logons, db_name='event_logons_02.db')
    save_to_database(logs=logoffs, db_name='event_logoffs_02.db')
    save_to_csv(query_database(db_name='event_logons_02.db'), filename=os.path.join(base_path, 'exported_logons.csv'))
    save_to_csv(query_database(db_name='event_logoffs_02.db'), filename=os.path.join(base_path, 'exported_logoffs.csv'))

    end_time = time.time()
    print(f"Time taken: {end_time - start_time} seconds")
