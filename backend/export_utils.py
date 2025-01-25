import json
import logging
import os
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
        # Convert data to a DataFrame
        df = pd.DataFrame(data)

        # Remove duplicates
        df_unique = df.drop_duplicates(keep='first')

        # Check if the file exists
        if not os.path.exists(filename):
            # If the file doesn't exist, create it
            df_unique.to_csv(filename, index=False)
            print(f"Data successfully exported to {filename} (created new file).")
        else:
            # If the file exists, append to it
            df_existing = pd.read_csv(filename)
            combined_df = pd.concat([df_existing, df_unique]).drop_duplicates(keep='first')
            combined_df.to_csv(filename, index=False)
            print(f"Data successfully appended to {filename}.")
    except Exception as e:
        print(f"Error saving data to CSV: {e}")
