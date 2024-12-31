import pandas as pd

# Load the CSV file
csv_file_path = 'data/preprocessed_csvs/combined_injuries.csv'
data = pd.read_csv(csv_file_path)

# Get unique positions
unique_positions = data['position'].unique()

# Print unique positions
print("Unique positions:")
for position in unique_positions:
    print(position)