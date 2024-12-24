import os
import pandas as pd
from collections import Counter

def get_positions_from_file(file_path):
    """Extract unique positions from a CSV file."""
    try:
        df = pd.read_csv(file_path)
        # Convert POS column to string and handle NaN
        positions = df['Position'].fillna('UNKNOWN').astype(str)
        return positions.tolist()
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return []

def print_all_positions():
    """Print all unique positions and their counts from all team files."""
    teams = ['arizona-cardinals']
    
    # Initialize counters
    defense_positions = Counter()
    offense_positions = Counter()
    special_teams_positions = Counter()
    
    for team in teams:
        # Check each type of file
        files = {
            'defense': os.path.join(team, 'defense_2023.csv'),
            'offense': os.path.join(team, 'offense_2023.csv'),
            'special-teams': os.path.join(team, 'special-teams_2023.csv')
        }
        
        for file_type, file_path in files.items():
            if os.path.exists(file_path):
                positions = get_positions_from_file(file_path)
                if file_type == 'defense':
                    defense_positions.update(positions)
                elif file_type == 'offense':
                    offense_positions.update(positions)
                else:
                    special_teams_positions.update(positions)
    
    # Print results with counts
    def print_positions(title, counter):
        print(f"\n{title}")
        print("-" * len(title))
        for pos, count in sorted(counter.items(), key=lambda x: (-x[1], x[0])):
            print(f"{pos}: {count}")
    
    print_positions("Defense Positions", defense_positions)
    print_positions("Offense Positions", offense_positions)
    print_positions("Special Teams Positions", special_teams_positions)

if __name__ == "__main__":
    print_all_positions()