import pandas as pd
from datetime import datetime

def calculate_age(birth_date, target_date):
    """Calculate age given birth date and target date."""
    if pd.isna(birth_date):
        return None
    try:
        birth = datetime.strptime(birth_date, '%Y-%m-%d')
        target = datetime.strptime(target_date, '%Y-%m-%d')
        age = target.year - birth.year - ((target.month, target.day) < (birth.month, birth.day))
        return age
    except (ValueError, TypeError):
        return None

def clean_and_transform_data(input_file, output_file):
    """
    Clean roster/contract data by removing specified columns and calculating age.
    """
    # Columns to keep
    columns_to_keep = [
        'player', 'year_signed', 'years', 'value', 'apy', 'guaranteed',
        'apy_cap_pct', 'inflated_value', 'inflated_apy', 'inflated_guaranteed',
        'gsis_id', 'season', 'team', 'position', 'depth_chart_position',
        'jersey_number', 'birth_date', 'draft_club', 'draft_number'
    ]
    
    # Read CSV
    df = pd.read_csv(input_file)
    
    # Keep only specified columns
    df = df[columns_to_keep]
    
    # Calculate age as of 4/25/2024
    df['age'] = df['birth_date'].apply(lambda x: calculate_age(x, '2024-04-25'))
    
    # Save cleaned data
    df.to_csv(output_file, index=False)
    print(f"Cleaned data saved to {output_file}")
    print(f"Total records: {len(df)}")
    print(f"Records with age calculated: {df['age'].notna().sum()}")

if __name__ == "__main__":
    input_file = "data/merged_contracts_roster_2023.csv"
    output_file = "data/cleaned_contracts_roster_2023.csv"
    
    clean_and_transform_data(input_file, output_file)