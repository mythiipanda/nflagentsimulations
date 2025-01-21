import pandas as pd

class PlayerAnalysis:
    def __init__(self, debug_dir, year):
        self.debug_dir = debug_dir
        self.year = year
        self.base_path = 'models/model/data/preprocessed_csvs/'
        
    def analyze_team_position(self, team, position):
        """Analyze calculation details for specific team and position."""
        try:
            # Load raw injuries data
            injuries_df = pd.read_csv(f'{self.debug_dir}/1_initial_injuries.csv')
            print("\n=== Raw Injuries Data ===")
            self._print_player_data(injuries_df, team, position, mapped=False)
            
            # Load mapped data
            mapped_df = pd.read_csv(f'{self.debug_dir}/3_mapped_positions_teams.csv')
            print("\n=== After Position/Team Mapping ===")
            self._print_player_data(mapped_df, team, position, mapped=True)
            
            # Find category and load stats
            category = self._get_category(position)
            if category:
                stats_df = pd.read_csv(f'{self.base_path}{category_mapping[category]["file"]}')
                stats_df = stats_df[stats_df['year'] == self.year]
                
                # Load merged data
                merged_df = pd.read_csv(f'{self.debug_dir}/5a_pre_calc_{category}.csv')
                print("\n=== Stats Data Match ===")
                self._print_stats_match(merged_df, team, position, category)
                
                # Load final calculations
                weighted_df = pd.read_csv(f'{self.debug_dir}/5b_player_weighted_{category}.csv')
                print("\n=== Final Calculations ===")
                self._print_calculations(weighted_df, team, position, category)
                
                # Show position group totals
                group_df = pd.read_csv(f'{self.debug_dir}/5c_position_group_{category}.csv')
                print("\n=== Position Group Totals ===")
                self._print_group_totals(group_df, team, position)
            
        except Exception as e:
            print(f"Error in analysis: {str(e)}")
    
    def _get_category(self, position):
        """Get category for position."""
        for category, details in category_mapping.items():
            if position in details['positions']:
                return category
        return None
        
    def _print_player_data(self, df, team, position, mapped=False):
        """Print player level data."""
        team_col = 'team' if not mapped else 'team_name'
        filtered = df[df[team_col] == team]
        if not filtered.empty:
            for _, row in filtered.iterrows():
                print(f"\nPlayer: {row['full_name']}")
                print(f"Position: {row['position']}")
                print(f"Team: {row[team_col]}")
                print(f"Status: {row['report_status']}")
                if 'injury_score' in row:
                    print(f"Injury Score: {row['injury_score']}")
    
    def _print_stats_match(self, df, team, position, category):
        """Print stats data match."""
        filtered = df[
            (df['team_name'] == team) & 
            (df['position'] == position)
        ]
        if not filtered.empty:
            for _, row in filtered.iterrows():
                print(f"\nPlayer: {row['full_name']}")
                print(f"Games: {row['player_game_stat']}")
                print(f"Snaps: {row[category_mapping[category]['weighting_stat']]}")
    
    def _print_calculations(self, df, team, position, category):
        """Print calculation details."""
        filtered = df[
            (df['team_name'] == team) & 
            (df['position'] == position)
        ]
        if not filtered.empty:
            for _, row in filtered.iterrows():
                print(f"\nPlayer: {row['full_name']}")
                print(f"Injury Score: {row['injury_score']}")
                print(f"Snap Share: {row['snap_share']:.3f}")
                print(f"Weighted Score: {row['player_weighted_score']:.3f}")
    
    def _print_group_totals(self, df, team, position):
        """Print position group totals."""
        filtered = df[
            (df['team_name'] == team) & 
            (df['position'] == position)
        ]
        if not filtered.empty:
            row = filtered.iloc[0]
            print(f"Total Injury Score: {row['injury_score']:.2f}")
            print(f"Total Weighted Score: {row['weighted_injury_score']:.2f}")

if __name__ == "__main__":
    year = 2023
    analyzer = PlayerAnalysis(f'debug_output/{year}', year)
    analyzer.analyze_team_position('ARZ', 'QB')