import pandas as pd

# Define the required columns for each CSV file
column_map = {
    "data/processed_defense_summary.csv": [
        "player", "player_id", "position", "team_name", "player_game_count",
        "grades_coverage_defense", "grades_defense", "grades_defense_penalty",
        "grades_pass_rush_defense", "grades_run_defense", "grades_tackle",
        "snap_counts_defense", "year"
    ],
    "data/processed_offense_blocking_summary.csv": [
        "player", "player_id", "position", "team_name", "player_game_count",
        "grades_offense", "grades_pass_block", "grades_run_block", 
        "snap_counts_offense", "year"
    ],
    "data/processed_passing_summary.csv": [
        "player", "player_id", "position", "team_name", "player_game_count",
        "grades_hands_fumble", "grades_offense", "grades_pass", "grades_run",
        "dropbacks", "year"
    ],
    "data/processed_receiving_summary.csv": [
        "player", "player_id", "position", "team_name", "player_game_count",
        "grades_hands_drop", "grades_hands_fumble", "grades_offense", "grades_pass_block", "grades_pass_route",
        "pass_plays", "year"
    ],
    "data/processed_rushing_summary.csv": [
        "player", "player_id", "position", "team_name", "player_game_count",
        "grades_hands_fumble", "grades_offense", "grades_offense_penalty", "grades_pass", "grades_pass_block", "grades_pass_route", "grades_run", "grades_run_block",
        "attempts", "year"        
    ]
}

# Function to preprocess a single CSV file
def preprocess_file(file_name, columns):
    try:
        # Read the file
        df = pd.read_csv(file_name)
        
        # Retain only the specified columns
        df = df[columns]
        
        # Save the processed file
        output_file = f"processed_{file_name}"
        df.to_csv(output_file, index=False)
        print(f"Processed and saved: {output_file}")
    except Exception as e:
        print(f"Error processing {file_name}: {e}")

# Preprocess each file
for file_name, columns in column_map.items():
    preprocess_file(file_name, columns)
