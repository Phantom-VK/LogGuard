import time
from collections import defaultdict
from datetime import datetime

from backend.analyzer import save_to_json
from database.toCSV import query_database, save_to_csv
from backend.event_logger import get_session_logs
from database.logdb import save_to_database

if __name__ == '__main__':

    # Example usage with minutes
    print("Analyzing recent login activity...")
    start_time = time.time()
    logons, logoffs = get_session_logs(days_back=10)
    # print(logons)
    # print(logoffs)
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

    # Save logs with timestamp in filename
    output_file = save_to_json(logons, filename='session_logons.json')
    output_file2 = save_to_json(logoffs, filename='session_logoffs.json')
    save_to_database(logs=logons, db_name='event_logons_02.db')
    save_to_database(logs=logoffs, db_name='event_logoffs_02.db')
    save_to_csv(query_database(db_name='event_logons_02.db'), filename='exported_logons.csv')
    save_to_csv(query_database(db_name='event_logoffs_02.db'), filename='exported_logoffs.csv')
    end_time = time.time()
    # print(f"\nDetailed logs saved to {output_file} & {output_file2}")
    print(f"Time taken ${end_time - start_time}")
