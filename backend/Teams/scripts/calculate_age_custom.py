import pandas as pd
from datetime import datetime

def calculate_age(birth_date, target_date=datetime(2024, 4, 25)):
    """Calculate age as of target date"""
    birthdate = pd.to_datetime(birth_date)
    age = target_date.year - birthdate.year
    if birthdate.month > target_date.month or (birthdate.month == target_date.month and birthdate.day > target_date.day):
        age -= 1
    return age

def main():
    # Read the roster data
    df = pd.read_csv('data/roster_data_2023.csv')
    
    # Add age column to original dataframe
    df['age'] = df['birth_date'].apply(calculate_age)
    
    # Save updated dataframe back to original CSV
    df.to_csv('data/roster_data_2023.csv', index=False)
    print("Age column added to roster_data_2023.csv")

if __name__ == "__main__":
    main()