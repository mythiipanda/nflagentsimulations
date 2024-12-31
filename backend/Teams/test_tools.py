import os
import sqlite3
import unittest
from typing import List, Tuple, Optional
import logging

# Import the functions from the corrected tools.py
import tools

# Configure logging
logging.basicConfig(level=logging.INFO)

class TestTools(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Define paths to the actual databases
        cls.team_db_path = "arizona-cardinals/team_data.db"  # Path to Arizona Cardinals database
        cls.global_db_path = "global_database.db" # Path to your global database

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
        print(ranked_players_str)
        self.assertIn("Kyler Murray", ranked_players_str)  # Should be present
        self.assertIn("Zaven Collins", ranked_players_str)  # Should be present
        self.assertIn("James Conner", ranked_players_str)
        self.assertIn("HB:\n1. James Conner", ranked_players_str)  # Check ordering and position grouping
        self.assertNotIn("Error", ranked_players_str)

    def test_get_ranked_players_invalid_team(self):
        result = tools.get_ranked_players("Invalid Team", team_db_path=self.team_db_path)
        self.assertEqual(result, "Error: Unknown team name: Invalid Team")
        
    def test_get_player_stats_invalid_team_path(self):
        result = tools.get_player_stats("Kyler Murray", team_db_path="invalid_path.db")
        self.assertEqual(result, "Error: Team database not found")
    
    def test_get_position_stats_invalid_position(self):
        result = tools.get_position_stats("Arizona Cardinals", "XX", team_db_path=self.team_db_path)
        self.assertEqual(result, "Error: No PFF position mapping found for roster position 'XX'.")

    def test_compare_players_invalid_player(self):
        result = tools.compare_players("Invalid Player", "Kyler Murray", team_db_path=self.team_db_path)
        self.assertEqual(result, "Player Invalid Player not found in the roster.")

    def test_get_position_group(self):
        position_group_str = tools.get_position_group("Arizona Cardinals", "HB", team_db_path=self.team_db_path)
        self.assertIn("James Conner", position_group_str)
        self.assertIn("Rank", position_group_str)
        self.assertIn("Grade", position_group_str)
        self.assertNotIn("Error", position_group_str)

    def test_get_position_group_invalid_team_path(self):
        result = tools.get_position_group("Arizona Cardinals", "QB", team_db_path="invalid_path.db")
        self.assertEqual(result, "Error: Team database not found")
    
    def test_query_team_stats(self):
        # Test with team name
        team_stats_str = tools.query_team_stats(db_path=self.global_db_path, team="Chicago Bears")
        self.assertIn("Chicago Bears", team_stats_str)  # Assuming data exists for Chicago Bears

        # Test with overall grade filter
        team_stats_str = tools.query_team_stats(db_path=self.global_db_path, min_overall=80)
        self.assertNotIn("No matching records found.", team_stats_str)  # Assuming some teams have overall >= 80

        # Test with multiple filters
        team_stats_str = tools.query_team_stats(db_path=self.global_db_path, team="New York Giants", min_overall=70, max_off=90)
        self.assertIn("New York Giants", team_stats_str)

        # Test with invalid team name
        team_stats_str = tools.query_team_stats(db_path=self.global_db_path, team="invalid-team")
        self.assertEqual(team_stats_str, "No matching records found.")
        
        # Test with space in team name
        team_stats_str = tools.query_team_stats(db_path=self.global_db_path, team="new york giants")
        self.assertIn("New York Giants", team_stats_str)

        # Test with no matching records
        team_stats_str = tools.query_team_stats(db_path=self.global_db_path, min_overall=100, max_overall=0)  # Impossible condition
        self.assertEqual(team_stats_str, "No matching records found.")

    def test_query_team_stats_invalid_db_path(self):
        result = tools.query_team_stats(db_path="invalid/path.db", team="Arizona Cardinals")
        self.assertEqual(result, "Error: Database path is invalid or does not exist.")

    def test_get_draft_order(self):
        draft_order_str = tools.get_draft_order(db_path=self.global_db_path)
        self.assertIn("Pick 1", draft_order_str)
        self.assertIn("Chicago Bears", draft_order_str)
        self.assertNotIn("Error", draft_order_str)

    def test_get_draft_order_invalid_db_path(self):
        result = tools.get_draft_order(db_path="invalid/path.db")
        self.assertEqual(result, "Error: Draft database not found")

    def test_make_draft_pick(self):
        # Test making a valid pick
        pick_result = tools.make_draft_pick("Arizona Cardinals", "Test Player", db_path=self.global_db_path)
        self.assertEqual(pick_result, "Arizona Cardinals selects Test Player with pick #4")

        # Verify that the pick is removed from draft_order
        conn = sqlite3.connect(self.global_db_path)
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
        pick_result = tools.make_draft_pick("Arizona Cardinals", "Another Player", db_path=self.global_db_path)
        self.assertIn("It is not Arizona Cardinals's turn to pick", pick_result)

        # Test making a pick when there are no more picks
        conn = sqlite3.connect(self.global_db_path)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM draft_order")  # Remove all remaining picks
        conn.commit()
        conn.close()

        pick_result = tools.make_draft_pick("Chicago Bears", "Player", db_path=self.global_db_path)
        self.assertEqual(pick_result, "No more picks available in draft order")

    def test_make_draft_pick_invalid_db_path(self):
        result = tools.make_draft_pick("Arizona Cardinals", "Test Player", db_path="invalid/path.db")
        self.assertEqual(result, "Error: Draft database not found")

if __name__ == '__main__':
    unittest.main()