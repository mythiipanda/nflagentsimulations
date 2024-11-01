import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Read the CSV files
rush_stats = pd.read_csv('../stats/player_stats_rush.csv')
pass_stats = pd.read_csv('../stats/player_stats_pass.csv')
rec_stats = pd.read_csv('../stats/player_stats_rec.csv')
def_stats = pd.read_csv('../stats/player_stats_def.csv')
rosters = pd.read_csv('../stats/rosters.csv')
rush_stats_head = rush_stats.head(5)
pass_stats_head = pass_stats.head(5)
rec_stats_head = rec_stats.head(5)
def_stats_head = def_stats.head(5)
rosters_head = rosters.head(5)
print("Rush Stats Head:\n", rush_stats_head)
print("Pass Stats Head:\n", pass_stats_head)
print("Rec Stats Head:\n", rec_stats_head)
print("Def Stats Head:\n", def_stats_head)
print("Rosters:\n", rosters)

rush_stats_head.to_csv('../stats/player_stats_rush_head.csv', index=False)
pass_stats_head.to_csv('../stats/player_stats_pass_head.csv', index=False)
rec_stats_head.to_csv('../stats/player_stats_rec_head.csv', index=False)
def_stats_head.to_csv('../stats/player_stats_def_head.csv', index=False)
rosters_head.to_csv('../stats/rosters_head.csv', index=False)