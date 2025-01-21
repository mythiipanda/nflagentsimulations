import pandas as pd
import os

def analyze_file_contents(file_path, file_type):
    """Get unique teams and positions from file."""
    try:
        # Read CSV and handle numeric values
        df = pd.read_csv(file_path)
        team_col = 'team_name' if file_type == 'stats' else 'team'
        
        # Convert team names to strings and clean
        if team_col in df.columns:
            df[team_col] = df[team_col].astype(str).str.strip()
            teams = sorted(df[df[team_col].str.len() > 0][team_col].unique())
        else:
            teams = []
            
        # Clean position data
        if 'position' in df.columns:
            df['position'] = df['position'].astype(str).str.strip()
            positions = sorted(df[df['position'].str.len() > 0]['position'].unique())
        else:
            positions = []
            
        return teams, positions
    
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return [], []

def print_analysis(file_path, file_type):
    """Print teams and positions."""
    teams, positions = analyze_file_contents(file_path, file_type)
    print(f"\nFile: {file_path}")
    print("Teams:", teams)
    print("Positions:", positions)
    print("-" * 80)

def main():
    files_to_analyze = {
        'injuries': 'models/model/data/preprocessed_csvs/combined_injuries.csv',
        'stats': [
            'models/model/data/preprocessed_csvs/preprocessed_defense_summary.csv',
            'models/model/data/preprocessed_csvs/preprocessed_passing_summary.csv',
            'models/model/data/preprocessed_csvs/preprocessed_receiving_summary.csv',
            'models/model/data/preprocessed_csvs/preprocessed_rushing_summary.csv',
            'models/model/data/preprocessed_csvs/preprocessed_offense_blocking_summary.csv'
        ]
    }
    
    print_analysis(files_to_analyze['injuries'], 'injuries')
    for stats_file in files_to_analyze['stats']:
        print_analysis(stats_file, 'stats')

if __name__ == "__main__":
    main()