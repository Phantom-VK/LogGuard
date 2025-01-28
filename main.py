import logging
import time
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from data_clean import clean_csv
from backend.event_logger import get_session_logs
from backend.export_utils import save_to_json, save_to_csv, save_json_file_to_csv
from database.db_utils import save_to_database, query_database
from enableEV import enable_failed_login_auditing

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler()
    ]
)


class LogAnalyzer:
    def __init__(self):
        self.logons: List[Dict] = []
        self.logoffs: List[Dict] = []
        self.start_time: float = 0
        self.export_dir = Path('exports')
        self.database_dir = Path('database')

    def setup_directories(self) -> None:
        """Create necessary directories if they don't exist."""
        try:
            self.export_dir.mkdir(exist_ok=True)
            self.database_dir.mkdir(exist_ok=True)
        except Exception as e:
            logging.error(f"Failed to create directories: {e}")
            raise

    def collect_logs(self, days_back: int = 100) -> None:
        """Collect logs for the specified time period."""
        try:
            logging.info(f"Collecting logs for past {days_back} days...")
            enable_failed_login_auditing()
            self.logons, self.logoffs = get_session_logs(days_back=days_back)
            logging.info(f"Found {len(self.logons)} human user sessions")
        except Exception as e:
            logging.error(f"Error collecting logs: {e}")
            raise

    def analyze_time_range(self) -> Optional[Tuple[datetime, datetime]]:
        """Analyze the time range of collected logs."""
        if not self.logons:
            logging.warning("No logs found to analyze time range")
            return None

        try:
            first_log = datetime.strptime(self.logons[0]['timestamp'], '%Y-%m-%d %H:%M:%S')
            last_log = datetime.strptime(self.logons[-1]['timestamp'], '%Y-%m-%d %H:%M:%S')
            logging.info(f"Log time range: {first_log} to {last_log}")
            return first_log, last_log
        except Exception as e:
            logging.error(f"Error analyzing time range: {e}")
            return None

    def analyze_risk_distribution(self) -> Dict[int, int]:
        """Analyze risk score distribution in logs."""
        try:
            risk_groups = defaultdict(list)
            for log in self.logons:
                risk_groups[log.get('risk_score', 0)].append(log)

            distribution = {score: len(events) for score, events in risk_groups.items()}

            logging.info("Risk Score Distribution:")
            for score in sorted(distribution.keys()):
                logging.info(f"Risk Score {score}: {distribution[score]} events")

            return distribution
        except Exception as e:
            logging.error(f"Error analyzing risk distribution: {e}")
            return {}

    def export_data(self) -> Tuple[str, str]:
        """Export logs to files and database."""
        try:
            # Save to JSON
            logons_json = self.export_dir / 'session_logons.json'
            logoffs_json = self.export_dir / 'session_logoffs.json'
            json_file1 = save_to_json(self.logons, str(logons_json))
            json_file2 = save_to_json(self.logoffs, str(logoffs_json))

            # Save to database
            logons_db = self.database_dir / 'event_logons_02.db'
            logoffs_db = self.database_dir / 'event_logoffs_02.db'
            save_to_database(logs=self.logons, db_name=str(logons_db))
            save_to_database(logs=self.logoffs, db_name=str(logoffs_db))

            # Export to CSV
            save_to_csv(query_database(db_name=str(logons_db)), 'exported_logons.csv')
            save_to_csv(query_database(db_name=str(logoffs_db)), 'exported_logoffs.csv')
            save_json_file_to_csv(json_file1)
            clean_csv('exported_logs.csv')

            logging.info(f"Data exported successfully to {json_file1} & {json_file2}")
            return json_file1, json_file2
        except Exception as e:
            logging.error(f"Error exporting data: {e}")
            raise


def main():
    start_time = time.time()
    analyzer = LogAnalyzer()

    try:
        # Setup
        analyzer.setup_directories()

        # Collect and analyze logs
        analyzer.collect_logs(days_back=30)
        analyzer.analyze_time_range()
        analyzer.analyze_risk_distribution()

        # Export data
        json_file1, json_file2 = analyzer.export_data()

        # Calculate and log execution time
        execution_time = time.time() - start_time
        logging.info(f"Total execution time: {execution_time:.2f} seconds")

    except Exception as e:
        logging.error(f"Error in main execution: {e}")
        raise


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        logging.critical(f"Application failed: {e}")
        exit(1)
