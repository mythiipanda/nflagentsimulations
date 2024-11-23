import pandas as pd

csv_files = [
    "processed_data/processed_passing_summary.csv",
    "processed_data/processed_receiving_summary.csv",
    "processed_data/processed_offense_blocking_summary.csv",
    "processed_data/processed_rushing_summary.csv",
    "processed_data/processed_defense_summary.csv",
]

for file in csv_files:
    try:
        df = pd.read_csv(file)
        print(f"--- {file} ---")
        print(df.columns)
        print(df.head)
        print("\n")
    except FileNotFoundError:
        print(f"File not found: {file}\n")
