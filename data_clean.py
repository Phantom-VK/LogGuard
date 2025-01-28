import pandas as pd
from sklearn.preprocessing import LabelEncoder

input_csv_path = 'exported_logs'


def clean_csv(input_csv_path):
    """
    Cleans the input CSV file and returns the cleaned DataFrame.

    Steps performed:
    - Convert 'timestamp' column to datetime.
    - Apply Label Encoding to 'status', 'is_rapid_login', and 'is_business_hours'.

    Parameters:
    - input_csv_path (str): Path to the input CSV file.

    Returns:
    - pd.DataFrame: The cleaned DataFrame.
    """
    # Load the dataset
    df = pd.read_csv(input_csv_path)

    # Convert 'timestamp' column to datetime
    if 'timestamp' in df.columns:
        df['timestamp'] = pd.to_datetime(df['timestamp'], dayfirst=True)

    # Apply Label Encoding to specific columns
    label_columns = ['status', 'is_rapid_login', 'is_business_hours']
    for column in label_columns:
        if column in df.columns:
            df[column] = LabelEncoder().fit_transform(df[column])

    return df.to_csv('clean.csv')

# Example usage
# cleaned_df = clean_csv('exported_logs.csv')