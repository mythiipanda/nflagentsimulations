import pandas as pd

def merge_contracts_roster(contracts_file, roster_file, output_file):
    """
    Merge contracts and roster data in two steps:
    1. First match on valid gsis_id
    2. Then match remaining records on player/full_name
    """
    # Read files
    contracts_df = pd.read_csv(contracts_file)
    roster_df = pd.read_csv(roster_file)
    
    # Drop team from contracts if it exists
    if 'team' in contracts_df.columns:
        contracts_df = contracts_df.drop('team', axis=1)
    
    # Split contracts into those with and without gsis_id
    contracts_with_id = contracts_df[contracts_df['gsis_id'].notna()].copy()
    contracts_without_id = contracts_df[contracts_df['gsis_id'].isna()].copy()
    
    # First merge on valid gsis_ids
    id_merged = pd.merge(
        contracts_with_id,
        roster_df,
        on='gsis_id',
        how='inner'
    )
    
    # Then try to match remaining records by name
    name_merged = pd.merge(
        contracts_without_id,
        roster_df,
        left_on='player',
        right_on='full_name',
        how='inner'
    )
    
    # Combine both sets of matches
    merged_df = pd.concat([id_merged, name_merged], ignore_index=True)
    
    # Save result
    merged_df.to_csv(output_file, index=False)
    print(f"Records merged by gsis_id: {len(id_merged)}")
    print(f"Records merged by name: {len(name_merged)}")
    print(f"Total records merged: {len(merged_df)}")

if __name__ == "__main__":
    contracts_file = "data/active_contracts_2023.csv"
    roster_file = "data/roster_data_2023.csv" 
    output_file = "data/merged_contracts_roster_2023.csv"
    
    merge_contracts_roster(contracts_file, roster_file, output_file)