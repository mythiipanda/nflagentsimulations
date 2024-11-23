import os
import argparse
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

def create_visualizations_directory(directory='visualizations'):
    """Create visualizations directory if it doesn't exist."""
    if not os.path.exists(directory):
        os.makedirs(directory)

def load_data(filepath):
    """Load room grades data from CSV."""
    if not os.path.isfile(filepath):
        raise FileNotFoundError(f"The file {filepath} does not exist.")
    return pd.read_csv(filepath)

def filter_data_by_year(df, year):
    """Filter the DataFrame for a specific year."""
    filtered_df = df[df['year'] == year].copy()
    if filtered_df.empty:
        raise ValueError(f"No data found for the year {year}.")
    return filtered_df

def create_heatmap(df, grade_cols, year, output_dir):
    """Create and save a heatmap of position grades by team."""
    plt.figure(figsize=(15, 10))
    heatmap_data = df.set_index('team_name')[grade_cols]
    sns.heatmap(
        heatmap_data, 
        cmap='RdYlGn',
        center=0.6,  # Adjusted to reflect normalized scale
        vmin=0,
        vmax=1,
        annot=True,
        fmt='.2f',  # Display two decimal places for normalized grades
        cbar_kws={'label': 'Grade'},
        linewidths=0.5,
        linecolor='gray'
    )
    plt.title(f'{year} Position Room Grades by Team')
    plt.xticks(rotation=45, ha='right')
    plt.yticks(rotation=0)
    plt.tight_layout()
    filepath = os.path.join(output_dir, f'{year}_room_grades_heatmap.png')
    plt.savefig(filepath)
    plt.close()

def create_boxplot(df, positions, plot_title, output_filename, output_dir):
    """Create and save a boxplot for specified positions."""
    plt.figure(figsize=(15, 8))
    melted_data = df.melt(
        id_vars=['team_name'], 
        value_vars=positions,
        var_name='Position',
        value_name='Grade'
    )
    sns.boxplot(data=melted_data, x='Position', y='Grade', palette='Set3')
    plt.title(plot_title)
    plt.xlabel('Position')
    plt.ylabel('Grade')
    plt.xticks(rotation=45)
    plt.tight_layout()
    filepath = os.path.join(output_dir, output_filename)
    plt.savefig(filepath)
    plt.close()

def visualize_room_grades(year):
    """Generate visualizations for room grades of a specific year."""
    # Load the data
    df = load_data('processed_data/room_grades.csv')
    
    # Filter for the specified year
    df_year = filter_data_by_year(df, year)
    
    # Get position grade columns
    grade_cols = [col for col in df_year.columns if col.endswith('_grade')]
    
    # Separate offensive and defensive positions
    offensive_positions = [col for col in grade_cols if col.startswith(('QB', 'WR', 'TE', 'T', 'G', 'C', 'HB'))]
    defensive_positions = [col for col in grade_cols if col.startswith(('ED', 'DI', 'LB', 'CB', 'S'))]
    
    # Create heatmap
    create_heatmap(df_year, grade_cols, year, 'visualizations')
    
    # Create offensive boxplot
    create_boxplot(
        df_year, 
        offensive_positions, 
        f'{year} Offensive Position Grades Distribution',
        f'{year}_offensive_grades.png',
        'visualizations'
    )
    
    # Create defensive boxplot
    create_boxplot(
        df_year, 
        defensive_positions, 
        f'{year} Defensive Position Grades Distribution',
        f'{year}_defensive_grades.png',
        'visualizations'
    )

def parse_arguments():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description='Visualize Room Grades.')
    parser.add_argument('--year', type=int, default=2023, help='Year for which to generate visualizations.')
    parser.add_argument('--output_dir', type=str, default='visualizations', help='Directory to save visualizations.')
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_arguments()
    create_visualizations_directory(args.output_dir)
    
    try:
        visualize_room_grades(args.year)
        print(f"Visualizations for {args.year} have been successfully saved to '{args.output_dir}'.")
    except Exception as e:
        print(f"Error: {e}")