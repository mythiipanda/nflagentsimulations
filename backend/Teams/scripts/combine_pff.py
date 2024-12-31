import pandas as pd
import os

def combine_team_csvs():
    # Create data directory if it doesn't exist
    data_dir = "data"
    os.makedirs(data_dir, exist_ok=True)
    
    # List of teams
    teams = [
        "arizona-cardinals", "atlanta-falcons", "baltimore-ravens", "buffalo-bills",
        "carolina-panthers", "chicago-bears", "cincinnati-bengals", "cleveland-browns",
        "dallas-cowboys", "denver-broncos", "detroit-lions", "green-bay-packers",
        "houston-texans", "indianapolis-colts", "jacksonville-jaguars", "kansas-city-chiefs",
        "las-vegas-raiders", "los-angeles-rams", "los-angeles-chargers", "miami-dolphins",
        "minnesota-vikings", "new-england-patriots", "new-orleans-saints", "new-york-giants",
        "new-york-jets", "philadelphia-eagles", "pittsburgh-steelers", "san-francisco-49ers",
        "seattle-seahawks", "tampa-bay-buccaneers", "tennessee-titans", "washington-commanders"
    ]

    # Initialize empty dataframes
    defense_combined = pd.DataFrame()
    offense_combined = pd.DataFrame()
    special_teams_combined = pd.DataFrame()

    # Combine CSVs
    for team in teams:
        try:
            defense_path = os.path.join(team, "defense_2023.csv")
            if os.path.exists(defense_path):
                defense_df = pd.read_csv(defense_path)
                defense_df['Team'] = team
                defense_combined = pd.concat([defense_combined, defense_df], ignore_index=True)

            offense_path = os.path.join(team, "offense_2023.csv")
            if os.path.exists(offense_path):
                offense_df = pd.read_csv(offense_path)
                offense_df['Team'] = team
                offense_combined = pd.concat([offense_combined, offense_df], ignore_index=True)

            special_teams_path = os.path.join(team, "special_teams_2023.csv")
            if os.path.exists(special_teams_path):
                special_teams_df = pd.read_csv(special_teams_path)
                special_teams_df['Team'] = team
                special_teams_combined = pd.concat([special_teams_combined, special_teams_df], ignore_index=True)
                
        except Exception as e:
            print(f"Error processing {team}: {str(e)}")

    # Save combined files
    try:
        defense_combined.to_csv(os.path.join(data_dir, "defense_combined_2023.csv"), index=False)
        offense_combined.to_csv(os.path.join(data_dir, "offense_combined_2023.csv"), index=False)
        special_teams_combined.to_csv(os.path.join(data_dir, "special_teams_combined_2023.csv"), index=False)
        print("Files successfully saved to data directory")
    except Exception as e:
        print(f"Error saving files: {str(e)}")

if __name__ == "__main__":
    combine_team_csvs()