import sqlite3
import csv
import pandas as pd
Export_fields = [
    'timestamp',
    'event_type',
    'user',
    'domain',
    'user_sid',
    'account_type',
    'logon_type',
    'status',
    'failure_reason',
    'logon_id',
    'session_duration',
    'source_ip',
    'destination_ip',
    'workstation_name',
    'is_business_hours',
    'day_of_week',
    'hour_of_day',
    'elevated_token',
    'risk_factors',
    'risk_score',
    'authentication_method',
    'event_id',
    'event_task_category',
    'target_user_name',
    'caller_process_name'
]

def query_database(db_name, table_name='session_logs'):
    """
    Query all data from the specified database table.

    :param db_name: Name of the SQLite database file.
    :param table_name: Name of the table to query.
    :return: A list of dictionaries containing the query results.
    """
    try:
        # Connect to the SQLite database
        conn = sqlite3.connect(db_name)
        cursor = conn.cursor()

        # Execute query to fetch all rows from the table
        # cursor.execute(f"SELECT * FROM {table_name}")
        # rows = cursor.fetchall()

        fields_str = ', '.join(Export_fields)
        query = f"SELECT {fields_str} FROM {table_name}"
        cursor.execute(query)
        rows = cursor.fetchall()
        # Fetch column names
        # columns = [desc[0] for desc in cursor.description]

        # Convert rows into a list of dictionaries
        # data = [dict(zip(columns, row)) for row in rows]
        data = [dict(zip(Export_fields,row)) for row in rows]
        conn.close()
        return data
    except sqlite3.Error as e:
        print(f"Database error: {str(e)}")
        return []
    except Exception as e:
        print(f"Error querying database: {e}")
        return []


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



