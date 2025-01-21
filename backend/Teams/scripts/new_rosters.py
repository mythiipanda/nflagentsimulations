import pandas as pd
import os

def create_duplicate_names_dict():
    return {
        'Aaron Brewer': {'ARI': 'LS', 'TEN': 'OL'},
        'Anthony Brown': {'NYJ': 'DB', 'BAL': 'QB'},
        'Brandon Smith': {'ARI': 'WR', 'PHI': 'LB'},
        'Byron Young': {'LV': 'DL', 'LA': 'LB'},
        'Caleb Johnson': {'JAX': 'LB', 'ARI': 'LB'},
        'Connor McGovern': {'NYJ': 'OL', 'BUF': 'OL'},
        'D.J. Turner': {'LV': 'WR', 'CIN': 'DB'},
        'David Long': {'MIA': 'LB', 'GB': 'DB'},
        'Jaylon Jones': {'CHI': 'DB', 'IND': 'DB'},
        'Jaylon Moore': {'JAX': 'WR', 'SF': 'OL'},
        'Jonah Williams': {'CIN': 'OL', 'LA': 'DL'},
        'Josh Allen': {'BUF': 'QB', 'JAX': 'LB'},
        'Lamar Jackson': {'BAL': 'QB', 'CAR': 'DB'},
        'Michael Carter': {'NYJ': 'DB', 'ARI': 'RB'},
        'Michael Thomas': {'CIN': 'DB', 'NO': 'WR'},
        'Spencer Brown': {'CAR': 'RB', 'BUF': 'OL'}
    }

def get_position_category(position):
    defense_positions = ['DB', 'DL', 'LB']
    offense_positions = ['QB', 'RB', 'WR', 'TE', 'OL']
    special_teams_positions = ['K', 'P', 'LS']
    
    if position in defense_positions:
        return 'defense'
    elif position in offense_positions:
        return 'offense'
    elif position in special_teams_positions:
        return 'special_teams'
    return None

def standardize_name(name):
    """Standardize a name for comparison"""
    # Remove periods and extra spaces
    cleaned = name.replace('.', '')
    cleaned = ' '.join(cleaned.split())
    return cleaned.lower()

def are_names_matching(name1, name2):
    """Compare two names using standardized versions"""
    return standardize_name(name1) == standardize_name(name2)

def get_player_stats(player_name, current_team, global_stats, duplicate_names):
    """Get most relevant stats for player based on current team"""
    # Handle duplicate names first
    if player_name in duplicate_names:
        return global_stats[
            global_stats.apply(lambda x: are_names_matching(x['Player'], player_name) and x['Team'] == current_team, axis=1)
        ]

    # Get all entries for player using standardized comparison
    player_entries = global_stats[
        global_stats['Player'].apply(lambda x: are_names_matching(x, player_name))
    ]
    
    if len(player_entries) == 0:
        return None
    elif len(player_entries) == 1:
        return player_entries
    
    # Multiple entries - try current team first
    current_team_stats = player_entries[player_entries['Team'] == current_team]
    if len(current_team_stats) > 0:
        return current_team_stats
    
    # If no current team stats, get entry with most snaps
    if 'Snaps' in player_entries.columns:
        return player_entries.nlargest(1, 'Snaps')
    else:
        return player_entries.iloc[-1:]


def process_team_roster(team_folder, global_data, duplicate_names):
    roster_path = os.path.join(team_folder, 'roster.csv')
    if not os.path.exists(roster_path):
        return
    
    roster_df = pd.read_csv(roster_path)
    current_team = os.path.basename(team_folder)
    
    defense_players = []
    offense_players = []
    special_teams_players = []
    
    for _, player in roster_df.iterrows():
        full_name = player['full_name']
        position = player['position']
        category = get_position_category(position)
        
        if not category:
            continue
            
        global_stats = global_data[category]
        player_stats = get_player_stats(full_name, current_team, global_stats, duplicate_names)
        
        if player_stats is not None and not player_stats.empty:
            if category == 'defense':
                defense_players.append(player_stats.iloc[0])
            elif category == 'offense':
                offense_players.append(player_stats.iloc[0])
            elif category == 'special_teams':
                special_teams_players.append(player_stats.iloc[0])
    
    # Save results
    if defense_players:
        pd.DataFrame(defense_players).to_csv(os.path.join(team_folder, 'defense_2023.csv'), index=False)
    if offense_players:
        pd.DataFrame(offense_players).to_csv(os.path.join(team_folder, 'offense_2023.csv'), index=False)
    if special_teams_players:
        pd.DataFrame(special_teams_players).to_csv(os.path.join(team_folder, 'special_teams_2023.csv'), index=False)

def main():
    # Load global data
    global_data = {
        'defense': pd.read_csv('data/defense_combined_2023.csv'),
        'offense': pd.read_csv('data/offense_combined_2023.csv'),
        'special_teams': pd.read_csv('data/special_teams_combined_2023.csv')
    }
    
    duplicate_names = create_duplicate_names_dict()
    
    # Process each team
    teams = [d for d in os.listdir('.') if os.path.isdir(d) and d != 'data' and d != 'scripts' and d != '__pycache__']
    for team in teams:
        process_team_roster(team, global_data, duplicate_names)
        print(f"Processed {team}")

if __name__ == "__main__":
    main()