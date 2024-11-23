import pandas as pd
import numpy as np
import json
import os
def load_grade_weights(config_path='grade_weights.json'):
    """Load grade weights from a JSON configuration file."""
    if not os.path.isfile(config_path):
        raise FileNotFoundError(f"The configuration file {config_path} does not exist.")
    
    with open(config_path, 'r') as file:
        grade_weights = json.load(file)
    
    return grade_weights
def load_position_specific_data(position):
    """Load only relevant data for each position"""
    if position == 'QB':
        df = pd.read_csv('processed_data/processed_passing_summary.csv')
        return df[df['position'] == position]
    
    elif position in ['WR', 'TE']:
        df = pd.read_csv('processed_data/processed_receiving_summary.csv')
        return df[df['position'] == position]
    
    elif position in ['T', 'G', 'C']:
        df = pd.read_csv('processed_data/processed_offense_blocking_summary.csv')
        return df[df['position'] == position]
    
    elif position == 'HB':
        df = pd.read_csv('processed_data/processed_rushing_summary.csv')
        return df[df['position'] == position]
    
    elif position in ['ED', 'DI', 'LB', 'CB', 'S']:
        df = pd.read_csv('processed_data/processed_defense_summary.csv')
        return df[df['position'] == position]

def calculate_position_room_grades(df, position, grade_weights):
    """Calculate position-specific grades using weights from configuration."""
    
    if position not in grade_weights:
        raise ValueError(f"No grade weights defined for position: {position}")
    
    weights = grade_weights[position]
    
    # Calculate grades by multiplying each grade component with its weight
    grade_sum = 0
    grade_components = []
    for grade, weight in weights.items():
        if grade not in df.columns:
            raise ValueError(f"Column {grade} not found in DataFrame for position {position}.")
        grade_sum += df[grade] * weight
    
    # Normalize the grades by dividing by 100
    grades = grade_sum / 100
    
    # Calculate weights for weighted average (existing logic)
    # Example: weights = df['dropbacks'] / df['dropbacks'].sum()
    # This part remains unchanged
    if position == 'QB':
        weight_column = 'dropbacks'
    elif position == 'WR' or position == 'TE':
        weight_column = 'pass_plays'
    elif position == 'HB':
        weight_column = 'attempts'
    elif position in ['T', 'G', 'C']:
        weight_column = 'snap_counts_offense'
    elif position in ['ED', 'DI', 'LB', 'CB', 'S']:
        weight_column = 'snap_counts_defense'
    else:
        weight_column = None
    
    if weight_column and weight_column in df.columns:
        weights = df[weight_column] / df[weight_column].sum()
    else:
        weights = pd.Series([1] * len(df), index=df.index)
    
    # Calculate weighted average
    if weights.sum() == 0:
        return 0  # Avoid division by zero
    return (grades * weights).sum()


def calculate_room_grades(config_path='grade_weights.json'):
    positions = ['QB', 'WR', 'TE', 'T', 'G', 'C', 'HB', 'ED', 'DI', 'LB', 'CB', 'S']
    room_grades = []
    
    # Load grade weights from configuration
    grade_weights = load_grade_weights(config_path)
    
    for position in positions:
        # Load position-specific data
        position_df = load_position_specific_data(position)
        if position_df is None or len(position_df) == 0:
            continue
        
        # Calculate team grades for each year
        team_grades = position_df.groupby(['team_name', 'year']).apply(
            lambda x: calculate_position_room_grades(x, position, grade_weights)
        ).reset_index(name='room_grade')
        
        team_grades['position'] = position
        
        room_grades.append(team_grades)
    
    # Combine all room grades
    final_grades = pd.concat(room_grades, ignore_index=True)
    
    # Pivot the data to get one row per team-year with columns for each position
    pivoted_grades = final_grades.pivot_table(
        index=['team_name', 'year'],
        columns='position',
        values='room_grade'
    ).reset_index()
    
    # Rename columns to include '_grade' suffix
    position_columns = {pos: f'{pos}_grade' for pos in positions}
    pivoted_grades.rename(columns=position_columns, inplace=True)
    
    # Fill NaN grades with 0 (or another appropriate value)
    pivoted_grades.fillna(0, inplace=True)
    pivoted_grades.sort_values(['team_name', 'year'], inplace=True)
    
    return pivoted_grades

if __name__ == "__main__":
    final_grades = calculate_room_grades()
    final_grades.to_csv('processed_data/room_grades.csv', index=False)
    print("Room grades have been successfully calculated and saved to 'processed_data/room_grades.csv'.")