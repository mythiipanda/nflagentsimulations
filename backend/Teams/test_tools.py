import os
import sqlite3
import unittest
from typing import List, Tuple, Optional
import logging

# Assuming the original tools.py is in the same directory
import tools

# Configure logging
logging.basicConfig(level=logging.INFO)

class TestTools(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        # Create an in-memory database for testing
        cls.db_path = ":memory:"
        cls.team_db_path = "test_team.db"
        cls.conn = sqlite3.connect(cls.team_db_path)
        cls.create_test_tables(cls.conn)
        cls.populate_test_data(cls.conn)

    @classmethod
    def tearDownClass(cls):
        # Close the database connection
        cls.conn.close()
        # Clean up the test database file
        if os.path.exists(cls.team_db_path):
            os.remove(cls.team_db_path)

    @staticmethod
    def create_test_tables(conn):
        """Creates tables for testing."""
        cursor = conn.cursor()

        # Create the roster table
        cursor.execute("""
            CREATE TABLE roster (
                full_name TEXT,
                position TEXT,
                jersey_number INTEGER
            )
        """)

        # Create the offense table
        cursor.execute("""
            CREATE TABLE offense (
                Player TEXT,
                JerseyNumber INTEGER,
                Position TEXT,
                GamesPlayed REAL,
                OffenseOverallGrade REAL,
                OffenseTotalSnaps INTEGER
            )
        """)

        # Create the defense table
        cursor.execute("""
            CREATE TABLE defense (
                Player TEXT,
                JerseyNumber INTEGER,
                Position TEXT,
                GamesPlayed REAL,
                DefenseOverallGrade REAL,
                DefenseTotalSnaps INTEGER
            )
        """)
        
        # Create the special_teams table
        cursor.execute("""
            CREATE TABLE special_teams (
                Player TEXT,
                JerseyNumber INTEGER,
                Position TEXT,
                GamesPlayed REAL,
                SpecialTeamsOverallGrade REAL,
                SpecialTeamsTotalSnaps INTEGER
            )
        """)

        # Create the draft_order table (for global database)
        cursor.execute("""
            CREATE TABLE draft_order (
                "Pick No." INTEGER PRIMARY KEY,
                Team TEXT
            )
        """)

        # Create the picks table (for global database)
        cursor.execute("""
            CREATE TABLE picks (
                "Pick No." INTEGER,
                Team TEXT,
                Player TEXT,
                FOREIGN KEY ("Pick No.") REFERENCES draft_order("Pick No.")
            )
        """)

        conn.commit()

    @staticmethod
    def populate_test_data(conn):
        """Populates the test tables with sample data."""
        cursor = conn.cursor()
        # Insert sample data into the roster table
        roster_data = [
            ('Kyler Murray', 'QB', 1),
            ('James Conner', 'HB', 6),
            ('Rondale Moore', 'WR', 4),
            ('Zach Ertz', 'TE', 86),
            ('D.J. Humphries', 'T', 74),
            ('Zaven Collins', 'LB', 25),
            ('Budda Baker', 'S', 3),
            ('Matt Prater', 'K', 5),
            ('Greg Dortch', 'WR', 83),
            ('Paris Johnson Jr.', 'T', 70),
            ('Leki Fotu', 'DI', 95),
            ('Ezekiel Turner', 'LB', 47)
        ]
        cursor.executemany("INSERT INTO roster (full_name, position, jersey_number) VALUES (?, ?, ?)", roster_data)

        # Insert sample data into the offense table
        offense_data = [
            ('Kyler Murray', 1, 'QB', 8.0, 70.8, 538),
            ('James Conner', 6, 'HB', 13.0, 89.2, 531),
            ('Rondale Moore', 4, 'WR', 8.0, 53.6, 755),
            ('Zach Ertz', 86, 'TE', 10.0, 50.8, 295),
            ('D.J. Humphries', 74, 'T', 15.0, 62.5, 922),
            ('Paris Johnson Jr', 70, 'T', 17, 60.1, 1130),
            ('Greg Dortch', 83, 'WR', 16, 68.2, 399),
            ('Hjalte Froholdt', 72, 'C', 17, 64.1, 1123)
        ]
        cursor.executemany("INSERT INTO offense (Player, JerseyNumber, Position, GamesPlayed, OffenseOverallGrade, OffenseTotalSnaps) VALUES (?, ?, ?, ?, ?, ?)", offense_data)

        # Insert sample data into the defense table
        defense_data = [
            ('Zaven Collins', 25, 'ED', 17.0, 72.1, 636),
            ('Budda Baker', 3, 'S', 12.0, 64.8, 763),
            ('Leki Fotu', 95, 'DI', 11, 46.1, 297),
            ('Ezekiel Turner', 47, 'LB', 16, 39.4, 50),
            ('Jalen Thompson', 34, 'S', 15, 71.3, 938),
            ('Kyzir White', 7, 'LB', 11, 58.9, 708)
        ]
        cursor.executemany("INSERT INTO defense (Player, JerseyNumber, Position, GamesPlayed, DefenseOverallGrade, DefenseTotalSnaps) VALUES (?, ?, ?, ?, ?, ?)", defense_data)
        
        special_teams_data = [
            ('Matt Prater', 5, 'K', 17, 60.9, 139)
        ]
        cursor.executemany("INSERT INTO special_teams (Player, JerseyNumber, Position, GamesPlayed, SpecialTeamsOverallGrade, SpecialTeamsTotalSnaps) VALUES (?, ?, ?, ?, ?, ?)", special_teams_data)
        
        # Insert sample data into the draft_order table
        draft_order_data = [
            (1, 'Chicago Bears'),
            (2, 'Washington Commanders'),
            (3, 'New England Patriots'),
            (4, 'Arizona Cardinals')
        ]
        cursor.executemany("INSERT INTO draft_order (\"Pick No.\", Team) VALUES (?, ?)", draft_order_data)

        conn.commit()

    def test_normalize_team_name(self):
        self.assertEqual(tools.normalize_team_name("arizona-cardinals"), "arizona-cardinals")
        self.assertEqual(tools.normalize_team_name("Arizona Cardinals"), "arizona-cardinals")
        self.assertEqual(tools.normalize_team_name("Arizona Cardinals", for_display=True), "Arizona Cardinals")
        with self.assertRaises(ValueError):
            tools.normalize_team_name("invalid-team")

    def test_get_team_roster(self):
        roster_str = tools.get_team_roster("Arizona Cardinals", team_db_path=self.team_db_path)
        self.assertIn("Kyler Murray", roster_str)
        self.assertIn("James Conner", roster_str)
        self.assertNotIn("Error", roster_str)

    def test_get_player_stats(self):
        stats_str = tools.get_player_stats("Kyler Murray", team_db_path=self.team_db_path)
        self.assertIn("Overall Grade", stats_str)
        self.assertIn("Total Snaps", stats_str)
        self.assertNotIn("Error", stats_str)

        stats_str = tools.get_player_stats("Nonexistent Player", team_db_path=self.team_db_path)
        self.assertEqual(stats_str, "Player Nonexistent Player not found in the roster.")

    def test_get_ranked_players(self):
        ranked_players_str = tools.get_ranked_players("Arizona Cardinals", team_db_path=self.team_db_path)
        self.assertIn("Kyler Murray", ranked_players_str)  # Should be present
        self.assertIn("Zaven Collins", ranked_players_str)  # Should be present
        self.assertIn("HB:\n1. James Conner", ranked_players_str)  # Check ordering and position grouping
        self.assertNotIn("Error", ranked_players_str)
        
    def test_get_ranked_players_missing_data(self):
        # Test case for a player with missing stats
        conn = sqlite3.connect(self.team_db_path)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO roster (full_name, position, jersey_number) VALUES (?, ?, ?)", ('Missing Stats', 'WR', 99))
        conn.commit()
        conn.close()

        ranked_players_str = tools.get_ranked_players("Arizona Cardinals", team_db_path=self.team_db_path)
        self.assertIn("Missing Stats", ranked_players_str)
        self.assertIn("WR:\n", ranked_players_str)
        self.assertNotIn("Error", ranked_players_str)
        
    def test_get_ranked_players_no_stats(self):
        # Test case for a player with no stats at all
        conn = sqlite3.connect(self.team_db_path)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO roster (full_name, position, jersey_number) VALUES (?, ?, ?)", ('No Stats', 'LB', 98))
        conn.commit()
        conn.close()
        
        ranked_players_str = tools.get_ranked_players("Arizona Cardinals", team_db_path=self.team_db_path)
        self.assertIn("No Stats", ranked_players_str)
        self.assertIn("LB:\n", ranked_players_str)
        self.assertNotIn("Error", ranked_players_str)

    def test_get_position_stats(self):
        position_stats_str = tools.get_position_stats("Arizona Cardinals", "QB", team_db_path=self.team_db_path)
        self.assertIn("Kyler Murray", position_stats_str)
        self.assertIn("Grade", position_stats_str)
        self.assertIn("Snaps", position_stats_str)
        self.assertNotIn("Error", position_stats_str)

    def test_compare_players(self):
        comparison_str = tools.compare_players("Kyler Murray", "James Conner", team_db_path=self.team_db_path)
        self.assertIn("Kyler Murray", comparison_str)
        self.assertIn("James Conner", comparison_str)
        self.assertIn("Overall Grade", comparison_str)
        self.assertNotIn("Error", comparison_str)

    def test_get_position_group(self):
        position_group_str = tools.get_position_group("Arizona Cardinals", "HB", team_db_path=self.team_db_path)
        self.assertIn("James Conner", position_group_str)
        self.assertIn("Rank", position_group_str)
        self.assertIn("Grade", position_group_str)
        self.assertNotIn("Error", position_group_str)

    def test_query_team_stats(self):
        # Test with team name
        team_stats_str = tools.query_team_stats(db_path=self.db_path, team_name="Chicago Bears")
        self.assertIn("Chicago Bears", team_stats_str)  # Assuming data exists for Chicago Bears

        # Test with overall grade filter
        team_stats_str = tools.query_team_stats(db_path=self.db_path, min_overall=80)
        self.assertNotIn("No matching records found.", team_stats_str)  # Assuming some teams have overall >= 80

        # Test with multiple filters
        team_stats_str = tools.query_team_stats(db_path=self.db_path, team_name="new-york-giants", min_overall=70, max_off=90)
        self.assertIn("New York Giants", team_stats_str)

        # Test with invalid team name
        team_stats_str = tools.query_team_stats(db_path=self.db_path, team_name="invalid-team")
        self.assertEqual(team_stats_str, "No matching records found.")
        
        # Test with space in team name
        team_stats_str = tools.query_team_stats(db_path=self.db_path, team_name="new york giants")
        self.assertIn("New York Giants", team_stats_str)

        # Test with no matching records
        team_stats_str = tools.query_team_stats(db_path=self.db_path, min_overall=100, max_overall=0)  # Impossible condition
        self.assertEqual(team_stats_str, "No matching records found.")

    def test_get_draft_order(self):
        draft_order_str = tools.get_draft_order(db_path=self.db_path)
        self.assertIn("Pick 1", draft_order_str)
        self.assertIn("Chicago Bears", draft_order_str)
        self.assertNotIn("Error", draft_order_str)

    def test_make_draft_pick(self):
        # Test making a valid pick
        pick_result = tools.make_draft_pick("Arizona Cardinals", "Test Player", db_path=self.db_path)
        self.assertEqual(pick_result, "Arizona Cardinals selects Test Player with pick #4")

        # Verify that the pick is removed from draft_order
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM draft_order WHERE [Pick No.] = 4")
        result = cursor.fetchone()
        self.assertIsNone(result)  # Pick should no longer exist

        # Verify that the pick is added to picks
        cursor.execute("SELECT * FROM picks WHERE [Pick No.] = 4")
        result = cursor.fetchone()
        self.assertIsNotNone(result)
        self.assertEqual(result[1], "Arizona Cardinals")
        self.assertEqual(result[2], "Test Player")
        conn.close()

        # Test making a pick when it's not the team's turn
        pick_result = tools.make_draft_pick("Arizona Cardinals", "Another Player", db_path=self.db_path)
        self.assertIn("It is not Arizona Cardinals's turn to pick", pick_result)

        # Test making a pick when there are no more picks
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM draft_order")  # Remove all remaining picks
        conn.commit()
        conn.close()

        pick_result = tools.make_draft_pick("Chicago Bears", "Player", db_path=self.db_path)
        self.assertEqual(pick_result, "No more picks available in draft order")
        
    def test_get_ranked_players_invalid_team(self):
        result = tools.get_ranked_players("Invalid Team", team_db_path=self.team_db_path)
        self.assertEqual(result, "Error: Unknown team name: Invalid Team")

    def test_get_ranked_players_no_roster(self):
        conn = sqlite3.connect(self.team_db_path)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM roster")
        conn.commit()
        conn.close()
        result = tools.get_ranked_players("Arizona Cardinals", team_db_path=self.team_db_path)
        self.assertEqual(result, "Error: No roster found for Arizona Cardinals. Please check the database.")
    
    def test_get_player_stats_invalid_team_path(self):
        result = tools.get_player_stats("Kyler Murray", team_db_path="invalid_path.db")
        self.assertEqual(result, "Error: Team database not found")
    
    def test_get_position_stats_invalid_position(self):
        result = tools.get_position_stats("Arizona Cardinals", "XX", team_db_path=self.team_db_path)
        self.assertEqual(result, "Error: No PFF position mapping found for roster position 'XX'.")

    def test_compare_players_invalid_player(self):
        result = tools.compare_players("Invalid Player", "Kyler Murray", team_db_path=self.team_db_path)
        self.assertEqual(result, "Player Invalid Player not found in the roster.")

    def test_get_position_group_invalid_team_path(self):
        result = tools.get_position_group("Arizona Cardinals", "QB", team_db_path="invalid_path.db")
        self.assertEqual(result, "Error: Team database not found")
    
    def test_query_team_stats_invalid_db_path(self):
        result = tools.query_team_stats(db_path="invalid/path.db", team_name="Arizona Cardinals")
        self.assertEqual(result, "Error: Database path is invalid or does not exist.")
    
    def test_get_draft_order_invalid_db_path(self):
        result = tools.get_draft_order(db_path="invalid/path.db")
        self.assertEqual(result, "Error: Draft database not found")

    def test_make_draft_pick_invalid_db_path(self):
        result = tools.make_draft_pick("Arizona Cardinals", "Test Player", db_path="invalid/path.db")
        self.assertEqual(result, "Error: Draft database not found")

if __name__ == '__main__':
    unittest.main()