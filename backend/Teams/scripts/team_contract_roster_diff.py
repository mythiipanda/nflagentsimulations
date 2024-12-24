import pandas as pd
import os

def normalize_name(name):
    """Normalize player name for comparison"""
    return str(name).strip().lower()

def analyze_team_differences(team_folder):
    """Compare roster and contract files to find players in roster but missing from contracts."""
    roster_file = os.path.join(team_folder, "roster.csv")
    contract_file = os.path.join(team_folder, "contracts.csv")
    
    if not (os.path.exists(roster_file) and os.path.exists(contract_file)):
        return
    
    # Read files
    roster_df = pd.read_csv(roster_file)
    contract_df = pd.read_csv(contract_file)
    
    # Track matched players
    matched_players = set()
    
    # First match by gsis_id
    roster_with_id = roster_df[roster_df['gsis_id'].notna()]
    contract_with_id = contract_df[contract_df['gsis_id'].notna()]
    
    roster_ids = set(roster_with_id['gsis_id'])
    contract_ids = set(contract_with_id['gsis_id'])
    
    # Track players matched by ID
    matched_by_id = roster_ids.intersection(contract_ids)
    matched_players.update(roster_with_id[roster_with_id['gsis_id'].isin(matched_by_id)]['full_name'])
    
    # For remaining players, try matching by normalized name
    remaining_roster = roster_df[~roster_df['full_name'].isin(matched_players)]
    remaining_contracts = contract_df[~contract_df['player'].isin(matched_players)]
    
    roster_names = {normalize_name(name): name for name in remaining_roster['full_name']}
    contract_names = {normalize_name(name): name for name in remaining_contracts['player']}
    
    # Find truly missing players
    missing_players = []
    for norm_name, orig_name in roster_names.items():
        if norm_name not in contract_names:
            player_info = roster_df[roster_df['full_name'] == orig_name]
            if not player_info.empty:
                missing_players.append([
                    orig_name,
                    player_info['position'].iloc[0],
                    player_info['status'].iloc[0]
                ])
    
    if missing_players:
        team_name = os.path.basename(team_folder)
        print(f"\n{team_name}:")
        for player in missing_players:
            print(f"- {player[0]} ({player[1]}) - {player[2]}")

def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    for team_folder in os.listdir(base_dir):
        team_path = os.path.join(base_dir, team_folder)
        if os.path.isdir(team_path) and '-' in team_folder:
            analyze_team_differences(team_path)

if __name__ == "__main__":
    main()