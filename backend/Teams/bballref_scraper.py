# %%
!pip install unidecode
import pandas as pd
from unidecode import unidecode

# %%
#Per Game
years = range(1998, 2025)
# 1997-98 to 2023-24
frames = {f"url{y}": f"https://www.basketball-reference.com/leagues/NBA_{y}_per_poss.html" for y in years}
pl_frames = {}
for num, y in enumerate(years, start=1):
    df = pd.read_html(frames[f"url{y}"], encoding='utf-8')[0]
    df["Season"] = f"{y-1}-{y}"
    pl_frames[f"pl{num}"] = df
NBA_Player_DF = pd.concat(pl_frames).drop_duplicates()
NBA_Player_DF.drop(NBA_Player_DF[NBA_Player_DF['Rk'] == 'Rk'].index, inplace=True)
NBA_Player_DF.reset_index(drop=True, inplace=True)
# compression_opts = dict(method='zip', archive_name='NBA_Player_Stats.csv')
# NBA_Player_DF.to_csv('NBA_Player_Stats.zip', index=False, compression=compression_opts)
NBA_Player_DF.to_csv('NBA_Player_Stats_Per_Poss.csv', index=False)
NBA_Player_DF

# %%
# preprocessing, replacing missing values with 0, sorting
df = pd.read_csv('NBA_Player_Stats_Per_Poss.csv')
df = df[~df['Player'].str.contains('League Average', na=False)]
df.drop(columns=['Rk', 'Unnamed: 29'], inplace=True)
df.fillna(0, inplace=True)
df['Player'] = df['Player'].apply(unidecode)
traded_players = df[df['Tm'] == 'TOT'][['Player', 'Season']].drop_duplicates()
df = df.merge(traded_players, on=['Player', 'Season'], how='left', indicator=True)
df = df[(df['_merge'] == 'left_only') | (df['Tm'] == 'TOT')]
df.drop(columns=['_merge'], inplace=True)
df.sort_values(by=['Player', 'Season'], inplace=True)
df['Season'] = df['Season'].apply(lambda x: int(x.split('-')[1]) if int(x.split('-')[1]) > 50 else int(x.split('-')[1]))
position_mapping = {'PG': 1, 'SG': 2, 'SF': 3, 'PF': 4, 'C': 5}
df['Pos'] = df['Pos'].map(position_mapping)
# df.drop(columns=['Team'])
df.to_csv('preprocessed_stats_per_poss.csv', index=False)
print(df.head())

# %%
#more data manipulation
df = pd.read_csv('preprocessed_stats.csv')
position_mapping = {'PG': 1, 'SG': 2, 'SF': 3, 'PF': 4, 'C': 5}
df['Pos'] = df['Pos'].map(position_mapping)
df.to_csv('preprocessed_stats.csv', index=False)
df.drop(columns=['Team', ])
print(df.head())

# %%
#Per Game
years = range(1998, 2025)
# 1997-98 to 2023-24
frames = {f"url{y}": f"https://www.basketball-reference.com/leagues/NBA_{y}_advanced.html" for y in years}
pl_frames = {}
for num, y in enumerate(years, start=1):
    df = pd.read_html(frames[f"url{y}"], encoding='utf-8')[0]
    df["Season"] = f"{y-1}-{y}"
    pl_frames[f"pl{num}"] = df
NBA_Player_DF = pd.concat(pl_frames).drop_duplicates()
NBA_Player_DF.drop(NBA_Player_DF[NBA_Player_DF['Rk'] == 'Rk'].index, inplace=True)
NBA_Player_DF.reset_index(drop=True, inplace=True)
# compression_opts = dict(method='zip', archive_name='NBA_Player_Stats.csv')
# NBA_Player_DF.to_csv('NBA_Player_Stats.zip', index=False, compression=compression_opts)
NBA_Player_DF.to_csv('NBA_Player_Stats_Advanced.csv', index=False)
NBA_Player_DF

# %%
# preprocessing, replacing missing values with 0, sorting
df = pd.read_csv('NBA_Player_Stats_Advanced.csv')
df = df[~df['Player'].str.contains('League Average', na=False)]
df.drop(columns=['Rk', 'Unnamed: 24'], inplace=True)
df.fillna(0, inplace=True)
df['Player'] = df['Player'].apply(unidecode)
traded_players = df[df['Tm'] == 'TOT'][['Player', 'Season']].drop_duplicates()
df = df.merge(traded_players, on=['Player', 'Season'], how='left', indicator=True)
df = df[(df['_merge'] == 'left_only') | (df['Tm'] == 'TOT')]
df.drop(columns=['_merge'], inplace=True)
df.sort_values(by=['Player', 'Season'], inplace=True)
df['Season'] = df['Season'].apply(lambda x: int(x.split('-')[1]) if int(x.split('-')[1]) > 50 else int(x.split('-')[1]))
position_mapping = {'PG': 1, 'SG': 2, 'SF': 3, 'PF': 4, 'C': 5}
df['Pos'] = df['Pos'].map(position_mapping)
# df.drop(columns=['Team'])
df.to_csv('preprocessed_stats_advanced.csv', index=False)
print(df.head())

# %%
df_per_poss = pd.read_csv('preprocessed_stats_per_poss.csv')
df_advanced = pd.read_csv('preprocessed_stats_advanced.csv')
merged_df = pd.merge(df_per_poss, df_advanced, on=['Player', 'Season'], suffixes=['1','1'], how='inner')
merged_df = merged_df.loc[:, ~merged_df.columns.duplicated()]
merged_df.to_csv('merged_preprocessed_stats.csv', index=False)

# %%
# def calculate_pis(player_stats):
#     offensive_score = (
#         player_stats['PER'] * 0.3 +
#         player_stats['TS%'] * 100 * 0.2 +
#         player_stats['AST%'] * 0.15 +
#         player_stats['USG%'] * 0.1 +
#         player_stats['OBPM'] * 2
#     )
#     defensive_score = (
#         player_stats['DRB%'] * 0.2 +
#         player_stats['STL%'] * 0.15 +
#         player_stats['BLK%'] * 0.15 +
#         player_stats['DBPM'] * 2
#     )
#     overall_impact = (
#         player_stats['WS/48'] * 100 * 0.3 +
#         player_stats['BPM'] * 2 +
#         player_stats['VORP'] * 5
#     )
#     pis = (offensive_score * 0.4 + defensive_score * 0.3 + overall_impact * 0.3) / 10
#     return pis
# df = pd.read_csv('merged_preprocessed_stats.csv')
# df['PIS'] = df.apply(calculate_pis, axis=1)
# df.to_csv('dataset_PIS.csv', index=False)

# %%
# remove data with low games played, etc
df = pd.read_csv('merged_preprocessed_stats.csv')
df.drop(columns=['Tm1'], inplace=True)
df_filtered = df[df['G1'] >= 30]
player_season_counts = df_filtered['Player'].value_counts()
players_to_keep = player_season_counts[player_season_counts > 3].index
df_filtered = df_filtered[df_filtered['Player'].isin(players_to_keep)]
df_filtered.rename(columns={'Pos1': 'Pos', 'Age1': 'Age', 'G1': 'G', 'MP1': 'MP'}, inplace=True)
df_filtered.to_csv('filtered_dataset.csv', index=False)

# %%


# %%



