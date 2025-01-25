import json
import logging

import pandas as pd


def save_to_json(logs, filename):
    """Save logs to JSON format."""
    try:
        with open(filename, 'w') as f:
            json.dump(logs, f, indent=2)
        logging.info(f"Logs saved to {filename}")
    except Exception as e:
        logging.error(f"Failed to save logs: {e}")


def save_to_csv(data, filename='exported_logs.csv'):
    """
    Save queried data to a CSV file.

    :param data: List of dictionaries containing the data to export.
    :param filename: Name of the output CSV file.
    """
    if not data:
        print("No data to save to CSV.")
        return

    try:
        # Write data to CSV
        # with open(filename, 'w', newline='', encoding='utf-8') as f:
        #     writer = csv.DictWriter(f, fieldnames=data[0].keys())
        #     writer.writeheader()
        #     writer.writerows(data)
        # print(f"Data successfully exported to {filename}")
        df = pd.DataFrame(data)
        df_unique = df.drop_duplicates(keep='first')
        df_unique.to_csv(filename,index=False)
        print(f"Data successfully exported to {filename}")
    except Exception as e:
        print(f"Error saving data to CSV: {e}")
