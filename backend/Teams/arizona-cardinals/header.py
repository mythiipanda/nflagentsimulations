import os
import pandas as pd

def print_csv_headers(folder_path):
    for file_name in os.listdir(folder_path):
        if file_name.endswith('.csv'):
            file_path = os.path.join(folder_path, file_name)
            df = pd.read_csv(file_path)
            headers = df.columns.tolist()
            print(f"CSV File: {file_name}")
            print("Headers:", headers)
            print("-------------------------")

folder_path = 'arizona-cardinals'
print_csv_headers(folder_path)