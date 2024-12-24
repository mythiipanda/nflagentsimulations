import pandas as pd
import os

def create_team_mapping():
    """Create mapping between folder names and team abbreviations."""
    return {
        "arizona-cardinals": "ARI",
        "atlanta-falcons": "ATL", 
        "baltimore-ravens": "BAL",
        "buffalo-bills": "BUF",
        "carolina-panthers": "CAR",
        "chicago-bears": "CHI",
        "cincinnati-bengals": "CIN",
        "cleveland-browns": "CLE",
        "dallas-cowboys": "DAL",
        "denver-broncos": "DEN",
        "detroit-lions": "DET",
        "green-bay-packers": "GB",
        "houston-texans": "HOU",
        "indianapolis-colts": "IND",
        "jacksonville-jaguars": "JAX",
        "kansas-city-chiefs": "KC",
        "las-vegas-raiders": "LV",
        "los-angeles-rams": "LA",
        "los-angeles-chargers": "LAC",
        "miami-dolphins": "MIA",
        "minnesota-vikings": "MIN",
        "new-england-patriots": "NE",
        "new-orleans-saints": "NO",
        "new-york-giants": "NYG",
        "new-york-jets": "NYJ",
        "philadelphia-eagles": "PHI",
        "pittsburgh-steelers": "PIT",
        "san-francisco-49ers": "SF",
        "seattle-seahawks": "SEA",
        "tampa-bay-buccaneers": "TB",
        "tennessee-titans": "TEN",
        "washington-commanders": "WAS"
    }

def split_by_team(input_file, team_folder_base, file_type):
    """Split input CSV by team and save to team folders."""
    df = pd.read_csv(input_file)
    team_mapping = create_team_mapping()
    
    # Create reverse mapping from abbreviation to folder name
    abbrev_to_folder = {v: k for k, v in team_mapping.items()}
    
    for team_abbrev in team_mapping.values():
        # Filter data for current team
        team_data = df[df['team'] == team_abbrev]
        
        if len(team_data) > 0:
            # Create team folder path
            team_folder = os.path.join(team_folder_base, abbrev_to_folder[team_abbrev])
            os.makedirs(team_folder, exist_ok=True)
            
            # Save team specific file
            output_file = os.path.join(team_folder, f'{file_type}.csv')
            team_data.to_csv(output_file, index=False)
            print(f"Saved {file_type} for {team_abbrev} ({len(team_data)} records)")

def main():
    # Base paths
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    team_folder_base = os.path.join(base_dir, "")
    
    # Input files
    contracts_file = os.path.join(base_dir, "data", "cleaned_contracts_roster_2023.csv")
    roster_file = os.path.join(base_dir, "data", "roster_data_2023.csv")
    
    # Process both files
    # split_by_team(contracts_file, team_folder_base, "contracts")
    split_by_team(roster_file, team_folder_base, "roster")

if __name__ == "__main__":
    main()