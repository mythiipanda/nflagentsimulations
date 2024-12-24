import sqlite3
import pandas as pd
import os
import glob
import logging

def create_team_database(team_dir, team_db_name="team_data.db"):
    """Creates an SQLite database for a specific team and loads data from CSV files."""
    
    logging.info(f"Creating database for {team_dir}")
    db_path = os.path.join(team_dir, team_db_name)
    conn = sqlite3.connect(db_path)
    
    # List of specific files we want to process
    year = 2023
    target_files = [
        f"defense_{year}.csv",
        f"offense_{year}.csv",
        f"special_teams_{year}.csv",
        f"roster.csv",
    ]
    
    # Process each target file
    for file_name in target_files:
        file_path = os.path.join(team_dir, file_name)
        if os.path.exists(file_path):
            try:
                # Read CSV file
                df = pd.read_csv(file_path)
                
                # Create table name from file name (remove date and extension)
                table_name = os.path.splitext(file_name)[0] # Removes .csv
                table_name = table_name.replace('2023', '').strip('_') # Removes 2023
                
                # Write to database
                df.to_sql(table_name, conn, if_exists='replace', index=False)
                logging.info(f"Loaded {file_name} into {table_name} table")
            except Exception as e:
                logging.error(f"Error processing {file_name}: {str(e)}")
        else:
            logging.warning(f"File not found: {file_path}")
    
    conn.close()
    logging.info(f"Database creation completed for {team_dir}")

# Example usage:
if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    
    # Process individual team directories
    teams = [
          "arizona-cardinals",
          "atlanta-falcons",
          "baltimore-ravens",
          "buffalo-bills",
          "carolina-panthers",
          "chicago-bears",
          "cincinnati-bengals",
          "cleveland-browns",
          "dallas-cowboys",
          "denver-broncos",
          "detroit-lions",
          "green-bay-packers",
          "houston-texans",
          "indianapolis-colts",
          "jacksonville-jaguars",
          "kansas-city-chiefs",
          "las-vegas-raiders",
          "los-angeles-rams",
          "los-angeles-chargers",
          "miami-dolphins",
          "minnesota-vikings",
          "new-england-patriots",
          "new-orleans-saints",
          "new-york-giants",
          "new-york-jets",
          "philadelphia-eagles",
          "pittsburgh-steelers",
          "san-francisco-49ers",
          "seattle-seahawks",
          "tampa-bay-buccaneers",
          "tennessee-titans",
          "washington-commanders"
      ]
    for team in teams:
        if os.path.exists(team):
            create_team_database(team)
        else:
            logging.error(f"Team directory not found: {team}")