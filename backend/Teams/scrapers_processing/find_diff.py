import pandas as pd

def analyze_merge_differences(contracts_file, roster_file, output_file):
    """Identify players missing from both gsis_id and name matches"""
    
    contracts_df = pd.read_csv(contracts_file)
    roster_df = pd.read_csv(roster_file)
    
    # First check gsis_id matches
    contracts_df_with_id = contracts_df[contracts_df['gsis_id'].notna()]
    roster_df_with_id = roster_df[roster_df['gsis_id'].notna()]
    
    contract_ids = set(contracts_df_with_id['gsis_id'])
    roster_ids = set(roster_df_with_id['gsis_id'])
    
    # Get records missing by ID
    missing_ids = roster_ids - contract_ids
    players_missing_by_id = roster_df[roster_df['gsis_id'].isin(missing_ids)]
    
    # From those missing by ID, check which ones also don't match by name
    contract_names = set(contracts_df['player'])
    completely_missing = players_missing_by_id[
        ~players_missing_by_id['full_name'].isin(contract_names)
    ][['gsis_id', 'full_name', 'team']]
    
    # Display results
    print("\nPlayers missing from both gsis_id and name matches:")
    print(completely_missing.to_string())
    print(f"\nTotal completely missing players: {len(completely_missing)}")

if __name__ == "__main__":
    contracts_file = "data/active_contracts_2023.csv"
    roster_file = "data/roster_data_2023.csv" 
    output_file = "data/merged_contracts_roster_2023.csv"
    
    analyze_merge_differences(contracts_file, roster_file, output_file)