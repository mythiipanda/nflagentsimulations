import os
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

def load_injury_metrics(filepath):
    """Load injury metrics data from CSV."""
    if not os.path.isfile(filepath):
        raise FileNotFoundError(f"The file {filepath} does not exist.")
    return pd.read_csv(filepath)

def filter_recent_years(df, years=3):
    """Filter the DataFrame to include only the most recent specified number of years."""
    max_year = df['season'].max()
    recent_years = range(max_year - years + 1, max_year + 1)
    return df[df['season'].isin(recent_years)]

def calculate_weighted_metrics(df):
    """Calculate weighted injury metrics based on snaps played."""
    # If a player hasn't shown up on the injury report, they are fully healthy (100%)
    df['percent_games_played'] = df['percent_games_played'].fillna(100)

    # Ensure snaps played are considered in the weighting
    if 'snaps_played' not in df.columns:
        raise ValueError("Column 'snaps_played' is required for weighting.")

    # Group by team, season, and position, weighting by snaps played
    weighted_metrics = (
        df.groupby(['team', 'season', 'position'])
        .apply(lambda x: (x['percent_games_played'] * x['snaps_played']).sum() / x['snaps_played'].sum() if x['snaps_played'].sum() > 0 else 100)
        .reset_index(name='weighted_percent_games_played')
    )

    return weighted_metrics

def pivot_weighted_metrics(weighted_metrics):
    """Pivot the weighted injury metrics to match the heatmap format."""
    pivoted_metrics = weighted_metrics.pivot_table(
        index=['team', 'season'],
        columns='position',
        values='weighted_percent_games_played'
    ).reset_index()

    # Rename columns to include '_injury_metric' suffix
    pivoted_metrics.rename(columns={col: f'{col}_injury_metric' for col in pivoted_metrics.columns if col not in ['team', 'season']}, inplace=True)

    # Fill missing values with 100 (fully healthy)
    pivoted_metrics.fillna(100, inplace=True)

    return pivoted_metrics

def create_injury_heatmap(df, injury_cols, year, output_dir):
    """Create and save a heatmap for injury metrics by team."""
    plt.figure(figsize=(15, 10))
    
    # Filter data for the specific year
    df_year = df[df['season'] == year].set_index('team')[injury_cols]
    
    # Create the heatmap
    sns.heatmap(
        df_year,
        cmap='RdYlGn',
        center=90,  # Assuming that higher values (closer to 100) are better
        annot=True,
        fmt='.1f',
        cbar_kws={'label': '% Games Played (Weighted)'},
        linewidths=0.5,
        linecolor='gray'
    )
    
    plt.title(f'{year} Weighted Injury Metrics Heatmap by Team')
    plt.xticks(rotation=45, ha='right')
    plt.yticks(rotation=0)
    plt.tight_layout()
    
    # Save the heatmap
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    filepath = os.path.join(output_dir, f'{year}_injury_metrics_heatmap.png')
    plt.savefig(filepath)
    plt.close()

def visualize_injury_metrics(year):
    """Generate a heatmap for injury metrics of a specific year."""
    # Use a relative path for consistency with other scripts
    injury_metrics_file = 'model/data/preprocessed_csvs/combined_injuries.csv'

    # Debug the resolved absolute path (optional)
    print(f"Resolved file path: {os.path.abspath(injury_metrics_file)}")

    # Load the injury metrics data load_injury_metrics(injury_metrics_file)

    # Filter to the most recent 3 years
    df = filter_recent_years(df, years=3)

    # Calculate weighted metrics
    weighted_metrics = calculate_weighted_metrics(df)

    # Pivot the data for heatmap compatibility
    pivoted_metrics = pivot_weighted_metrics(weighted_metrics)

    # Get injury metric columns
    injury_cols = [col for col in pivoted_metrics.columns if col.endswith('_injury_metric')]

    # Create heatmap
    create_injury_heatmap(pivoted_metrics, injury_cols, year, 'visualizations')

if __name__ == "__main__":
    # Change this year to the desired season for visualization
    target_year = 2024
    try:
        visualize_injury_metrics(target_year)
        print(f"Heatmap for {target_year} injury metrics has been saved in 'visualizations/'.")
    except Exception as e:
        print(f"Error: {e}")
