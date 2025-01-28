# export_utils.py
import json
import logging
import msvcrt  # Windows-specific file locking
import os
from contextlib import contextmanager
from pathlib import Path
from typing import List, Dict

import pandas as pd


@contextmanager
def windows_file_lock(file_handle):
    """Windows-compatible file locking context manager."""
    try:
        # Lock the file
        msvcrt.locking(file_handle.fileno(), msvcrt.LK_NBLCK, 1)
        yield
    finally:
        # Release the lock
        try:
            # Unlock the file
            msvcrt.locking(file_handle.fileno(), msvcrt.LK_UNLCK, 1)
        except:
            pass


def save_to_json(logs: List[Dict], filename: str) -> str:
    """
    Save logs to JSON format with Windows file locking.

    Args:
        logs: List of log dictionaries
        filename: Target file path
    Returns:
        str: Path to the saved file
    Raises:
        OSError: If file operations fail
        JSONDecodeError: If JSON serialization fails
    """
    filepath = Path(filename)
    try:
        # Create directory if it doesn't exist
        filepath.parent.mkdir(parents=True, exist_ok=True)

        # Open file in binary mode for Windows file locking
        with open(filepath, 'w+b') as f:
            with windows_file_lock(f):
                # Convert to JSON and write
                json_data = json.dumps(logs, indent=2).encode('utf-8')
                f.write(json_data)

        logging.info(f"Logs saved to {filename}")
        return str(filepath)
    except Exception as e:
        logging.error(f"Failed to save logs to JSON: {e}")
        raise


def save_to_csv(data, filename='exported_logs.csv'):
    """
    Save ML-relevant features to CSV.
    """
    if not data:
        print("No data to save to CSV.")
        return

    try:
        # Convert data to DataFrame
        df = pd.DataFrame(data)

        # Debug: Check if 'is_rapid_login' exists and is populated
        if 'is_rapid_login' not in df.columns:
            print("is_rapid_login column is missing from the data.")
        else:
            print(f"is_rapid_login values:\n{df['is_rapid_login'].value_counts()}")

        # Select ML-relevant columns
        ml_columns = [
            'timestamp',
            'user',
            'status',
            'is_rapid_login',
            'is_business_hours',
            'risk_score',
            'logon_type',
            'source_ip'
        ]

        # Filter columns and handle missing columns
        available_columns = [col for col in ml_columns if col in df.columns]
        df_ml = df[available_columns]

        # Remove duplicates
        df_unique = df_ml.drop_duplicates(keep='first')

        # Save to CSV
        if not os.path.exists(filename):
            df_unique.to_csv(filename, index=False)
            print(f"Created new file: {filename}")
        else:
            # Append to existing file
            df_existing = pd.read_csv(filename)
            combined_df = pd.concat([df_existing, df_unique]).drop_duplicates(keep='first')
            combined_df.to_csv(filename, index=False)
            print(f"Updated existing file: {filename}")
            print(f"Total records in file: {len(combined_df)}")

    except Exception as e:
        print(f"Error saving to CSV: {e}")


def save_json_file_to_csv(json_file_path, csv_file_path='exported_logs.csv'):
    """
    Load JSON data from a file, filter ML-relevant columns, and save to a CSV file.

    Args:
        json_file_path (str): Path to the JSON file containing log entries.
        csv_file_path (str): Path to the CSV file to save filtered data.
    """
    # Define ML-relevant columns to save
    ml_columns = [
        'timestamp',
        'user',
        'status',
        'is_rapid_login',
        'is_business_hours',
        'risk_score',
        'logon_type',
        'source_ip'
    ]

    try:
        # Load JSON data from the file
        with open(json_file_path, 'r') as f:
            json_data = json.load(f)

        # Convert JSON data to DataFrame
        df = pd.DataFrame(json_data)

        # Filter only the required ML columns
        available_columns = [col for col in ml_columns if col in df.columns]
        if not available_columns:
            print("No ML-relevant columns found in the JSON file.")
            return

        df_filtered = df[available_columns]

        # Ensure boolean columns (like is_rapid_login) are saved as True/False strings
        if 'is_rapid_login' in df_filtered.columns:
            df_filtered['is_rapid_login'] = df_filtered['is_rapid_login'].apply(lambda x: 'True' if x else 'False')

        # Remove duplicates
        df_filtered = df_filtered.drop_duplicates(keep='first')

        # Save to CSV
        if not df_filtered.empty:
            df_filtered.to_csv(csv_file_path, index=False)
            print(f"Data successfully saved to {csv_file_path}")
        else:
            print("No data to save after filtering.")
    except FileNotFoundError:
        print(f"File not found: {json_file_path}")
    except json.JSONDecodeError:
        print(f"Error decoding JSON from file: {json_file_path}")
    except Exception as e:
        print(f"Error saving JSON to CSV: {e}")
