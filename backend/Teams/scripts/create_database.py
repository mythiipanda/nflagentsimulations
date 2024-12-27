import sqlite3
import pandas as pd

def create_database(db_name="global.db"):
    """Creates an SQLite database with the required tables for the NFL draft simulation."""

    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    # --- Create the 'available_players' table ---
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS available_players (
            player_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            position TEXT,
            overall_rank REAL,
            height TEXT,
            weight INTEGER,
            college TEXT,
            birth_date TEXT,
            '33rd' TEXT,
            ATH TEXT,
            BR TEXT,
            Buzz TEXT,
            CBS TEXT,
            DT TEXT,
            ESPN TEXT,
            NBC TEXT,
            NFL TEXT,
            PFF TEXT,
            PFN TEXT,
            Ring TEXT,
            SBN TEXT,
            Tank TEXT,
            USA TEXT,
            WF TEXT,
            Yahoo TEXT,
            SD TEXT,
            Avg REAL
        )
        """
    )

    # --- Create the 'draft_order' table ---
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS draft_order (
            round INTEGER,
            pick INTEGER,
            team TEXT,
            PRIMARY KEY (round, pick)
        )
        """
    )

    # --- Create the 'draft_picks' table ---
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS draft_picks (
            year INTEGER,
            round INTEGER,
            pick INTEGER,
            team TEXT,
            player_id INTEGER,
            player_name TEXT,
            position TEXT,
            PRIMARY KEY (year, round, pick),
            FOREIGN KEY (player_id) REFERENCES available_players(player_id)
        )
        """
    )

    conn.commit()
    conn.close()
    print(f"Database '{db_name}' created successfully.")

def load_data(db_name="nfl_draft.db"):
    """Loads data from CSV files into the SQLite database."""

    conn = sqlite3.connect(db_name)

    # Load prospects_2024.csv
    try:
        prospects_df = pd.read_csv("data/prospects_2024.csv")
        prospects_df.columns = [
            col.replace("/", "_per_")
            .replace("%", "_percentage")
            .replace(".", "")
            .replace("#", "hashtag")
            .replace(" ", "_")
            .replace("\\r\\n", "_")
            .lower()
            for col in prospects_df.columns
        ]
        prospects_df.to_sql("available_players", conn, if_exists="replace", index=False)
        print("Data loaded into 'available_players' table.")
    except Exception as e:
        print(f"Error loading data into 'available_players' table: {e}")

    # Load draft-order.csv
    try:
        draft_order_df = pd.read_csv("data/draft-order.csv")
        draft_order_df.to_sql("draft_order", conn, if_exists="replace", index=False)
        print("Data loaded into 'draft_order' table.")
    except Exception as e:
        print(f"Error loading data into 'draft_order' table: {e}")

    # Load nfl_teams_2023.csv
    try:
        teams_df = pd.read_csv("data/nfl_teams_2023.csv")
        # team, needs - make sure these column names are correct after you create this
        teams_df.columns = [
            col.lower().replace(" ", "_") for col in teams_df.columns
        ]
        teams_df.to_sql("team_stats", conn, if_exists="replace", index=False)
        print("Data loaded into 'team_records' table.")
    except Exception as e:
        print(f"Error loading data into 'team_records' table: {e}")

    conn.close()

if __name__ == "__main__":
    create_database()
    load_data()