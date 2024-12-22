import pandas as pd
import os

# Set the data directory path
data_dir = "backend/data/"

# Get a list of all CSV files in the data directory
csv_files = [f for f in os.listdir(data_dir) if f.endswith(".csv")]

# Loop through each CSV file and print the head
for csv_file in csv_files:
    # Construct the full file path
    file_path = os.path.join(data_dir, csv_file)
    
    # Read the CSV file into a DataFrame
    df = pd.read_csv(file_path)
    
    # Print the name of the CSV file
    print(f"Data from {csv_file}:")
    
    # Print the head of the DataFrame
    print(df.head())
    print()
