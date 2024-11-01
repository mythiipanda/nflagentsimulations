import nfl_data_py as nfl
import pandas as pd
import os

# Create directory for saving stats if it doesn't exist
os.makedirs("stats", exist_ok=True)

# Specify the year of interest
years = [2024]

# 1. Pull team descriptive information
team_info = nfl.import_team_desc()
team_info.to_csv("stats/team_info.csv", index=False)

# 5. Pull roster data for each team
rosters = nfl.import_seasonal_rosters(years)
rosters.to_csv("stats/rosters.csv", index=False)

# 6. Pull individual player stats for each team
player_stats_pass = nfl.import_seasonal_pfr(s_type='pass', years=years)
player_stats_rush = nfl.import_seasonal_pfr(s_type='rush', years=years)
player_stats_rec = nfl.import_seasonal_pfr(s_type='rec', years=years)
player_stats_def = nfl.import_seasonal_pfr(s_type='def', years=years)



# Save player stats
player_stats_pass.to_csv("stats/player_stats_pass.csv", index=False)
player_stats_rush.to_csv("stats/player_stats_rush.csv", index=False)
player_stats_rec.to_csv("stats/player_stats_rec.csv", index=False)
player_stats_def.to_csv("stats/player_stats_def.csv", index=False)
