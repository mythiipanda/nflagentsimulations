import pandas as pd
import os

def clean_csv_files():
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

    csv_files = [
        "defense_2023.csv",
        "offense_2023.csv",
        "special_teams_2023.csv"
    ]

    for team in teams:
        for file_name in csv_files:
            file_path = os.path.join(team, file_name)
            if os.path.exists(file_path):
                try:
                    # Read and clean CSV
                    df = pd.read_csv(file_path)
                    df_cleaned = df.dropna(how='all')
                    
                    # Save cleaned file if rows were removed
                    if len(df) != len(df_cleaned):
                        df_cleaned.to_csv(file_path, index=False)
                        print(f"Cleaned {file_path}")
                        
                except Exception as e:
                    print(f"Error processing {file_path}: {str(e)}")

if __name__ == "__main__":
    clean_csv_files()