import pandas as pd

def find_duplicate_names():
    # Read the roster data
    df = pd.read_csv('data/roster_data_2023.csv')
    
    # Group by full name and count occurrences
    name_counts = df.groupby('full_name').size().reset_index(name='count')
    
    # Filter for names that appear more than once
    duplicates = name_counts[name_counts['count'] > 1]
    
    # Get detailed info for duplicate names
    for name in duplicates['full_name']:
        players = df[df['full_name'] == name]
        print(f"\n{name} appears {len(players)} times:")
        for _, player in players.iterrows():
            print(f"- Team: {player['team']}, Position: {player['position']}")

if __name__ == "__main__":
    find_duplicate_names()  