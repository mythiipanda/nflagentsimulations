import pandas as pd
import os
import glob

def clean_headers(base_directory, teams):
    """Remove category prefixes from column names and drop Rank column."""
    for team in teams:
        team_dir = os.path.join(base_directory, team)
        if not os.path.isdir(team_dir):
            print(f"Directory not found: {team}")
            continue
            
        for filename in glob.glob(os.path.join(team_dir, "*.csv")):
            try:
                # Get category from filename (e.g. "DEFENSE-COVERAGE")
                category = os.path.basename(filename).split('_')[1].upper()
                
                # Read CSV
                df = pd.read_csv(filename)
                
                # Clean column names
                new_columns = {}
                for col in df.columns:
                    # Remove category prefix and 2023
                    new_col = col.replace(f"{category}_", "")
                    new_columns[col] = new_col
                
                # Rename columns
                df.rename(columns=new_columns, inplace=True)
                
                # Drop Rank column if exists
                if 'Rank' in df.columns:
                    df.drop('Rank', axis=1, inplace=True)
                
                # Save changes
                df.to_csv(filename, index=False)
                print(f"Processed: {filename}")
                
            except Exception as e:
                print(f"Error processing {filename}: {e}")

# Example usage with same teams list
base_directory = "."
teams = [
    "arizona-cardinals", "atlanta-falcons", "baltimore-ravens",
    "buffalo-bills", "carolina-panthers", "chicago-bears",
    "cincinnati-bengals", "cleveland-browns", "dallas-cowboys",
    "denver-broncos", "detroit-lions", "green-bay-packers",
    "houston-texans", "indianapolis-colts", "jacksonville-jaguars",
    "kansas-city-chiefs", "las-vegas-raiders", "los-angeles-rams",
    "los-angeles-chargers", "miami-dolphins", "minnesota-vikings",
    "new-england-patriots", "new-orleans-saints", "new-york-giants",
    "new-york-jets", "philadelphia-eagles", "pittsburgh-steelers",
    "san-francisco-49ers", "seattle-seahawks", "tampa-bay-buccaneers",
    "tennessee-titans", "washington-commanders"
]

clean_headers(base_directory, teams)