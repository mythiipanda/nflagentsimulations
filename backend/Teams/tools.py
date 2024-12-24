# tools.py

import sqlite3
import os
import logging
from typing import List, Tuple, Optional

def get_team_roster(team_name: str, team_db_path: Optional[str] = None) -> str:
    """
    Retrieves the roster for a given team.
    """
    if not team_db_path or not os.path.exists(team_db_path):
        return f"Error: Database not found for {team_name}"

    try:
        conn = sqlite3.connect(team_db_path)
        cursor = conn.cursor()
        roster = []
        
        # Query all three tables to build complete roster
        for table in ['offense', 'defense', 'special-teams']:
            cursor.execute(f"SELECT Player, Position, JerseyNumber FROM '{table}'")
            results = cursor.fetchall()
            roster.extend(results)
        
        # Format roster data
        formatted_roster = [f"{player[0]} (#{player[2]}) - {player[1]}" for player in roster]
        return f"Roster for {team_name}:\n" + "\n".join(formatted_roster)

    except Exception as e:
        return f"Error retrieving roster: {e}"
    finally:
        if conn:
            conn.close()

def get_player_stats(player_name: str, db_path: Optional[str] = None, team_db_path: Optional[str] = None) -> str:
    """
    Retrieves stats for a given player.
    """
    if not team_db_path or not os.path.exists(team_db_path):
        return f"Error: Team database not found"

    try:
        conn = sqlite3.connect(team_db_path)
        cursor = conn.cursor()
        
        # Search in all three tables
        tables_and_columns = {
            'offense': ['Player', 'Position', 'GamesPlayed', 'OffenseOverallGrade', 'OffenseTotalSnaps'],
            'defense': ['Player', 'Position', 'GamesPlayed', 'DefenseOverallGrade', 'DefenseTotalSnaps'],
            'special-teams': ['Player', 'Position', 'GamesPlayed', 'SpecialTeamsOverallGrade', 'SpecialTeamsTotalSnaps']
        }
        
        for table, columns in tables_and_columns.items():
            columns_str = ', '.join(columns)
            cursor.execute(f"SELECT {columns_str} FROM '{table}' WHERE LOWER(Player) LIKE ?", 
                         ('%' + player_name.lower() + '%',))
            result = cursor.fetchone()
            
            if result:
                return (f"Player: {result[0]}\n"
                       f"Position: {result[1]}\n"
                       f"Games Played: {result[2]}\n"
                       f"Overall Grade: {result[3]}\n"
                       f"Total Snaps: {result[4]}")
        
        return f"Player {player_name} not found in the database."

    except Exception as e:
        return f"Error retrieving stats: {e}"
    finally:
        if conn:
            conn.close()

def get_draft_order(db_path: Optional[str] = None) -> str:
    """
    Retrieves the current draft order.
    """
    if not db_path or not os.path.exists(db_path):
        return "Error: Draft database not found"

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT [Pick No.], Team FROM draft_order ORDER BY [Pick No.]")
        order = cursor.fetchall()
        
        if not order:
            return "No draft picks found."
            
        formatted_order = [f"Pick {pick}: {team}" for pick, team in order]
        return "Current draft order:\n" + "\n".join(formatted_order)

    except Exception as e:
        return f"Error retrieving draft order: {e}"
    finally:
        if conn:
            conn.close()

def get_remaining_needs(team_name: str, team_db_path: Optional[str] = None) -> str:
    """
    Analyzes a team's roster and identifies positional needs.
    """
    if not team_db_path or not os.path.exists(team_db_path):
        return f"Error: Team database not found for {team_name}"

    try:
        conn = sqlite3.connect(team_db_path)
        cursor = conn.cursor()
        
        # Get position counts across all tables
        position_counts = {}
        for table in ['offense', 'defense', 'special-teams']:
            cursor.execute(f"SELECT Position, COUNT(*) FROM '{table}' GROUP BY Position")
            for position, count in cursor.fetchall():
                position_counts[position] = position_counts.get(position, 0) + count
        
        # Analyze needs based on position counts
        needs = []
        position_thresholds = {
            'QB': 3, 'RB': 4, 'WR': 6, 'TE': 3, 'OL': 8,
            'DL': 6, 'LB': 6, 'CB': 6, 'S': 4
        }
        
        for pos, threshold in position_thresholds.items():
            if pos not in position_counts or position_counts[pos] < threshold:
                needs.append(pos)
        
        if needs:
            return f"Remaining needs for {team_name}: {', '.join(needs)}"
        return f"No critical positional needs identified for {team_name}"

    except Exception as e:
        return f"Error analyzing team needs: {e}"
    finally:
        if conn:
            conn.close()

def make_draft_pick(team_name: str, player_name: str, db_path: Optional[str] = None, team_db_path: Optional[str] = None) -> str:
    """
    Makes a draft pick.
    """
    if not db_path or not os.path.exists(db_path):
        return "Error: Draft database not found"

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Check current draft position
        cursor.execute("SELECT [Pick No.], Team FROM draft_order ORDER BY [Pick No.] LIMIT 1")
        result = cursor.fetchone()
        if not result:
            return "No more picks available in draft order"
        
        pick_no, current_team = result
        if current_team != team_name:
            return f"It is not {team_name}'s turn to pick. Current pick belongs to {current_team}"

        # Verify player is available
        cursor.execute("SELECT name, position FROM available_players WHERE LOWER(name) LIKE ?",
                      ('%' + player_name.lower() + '%',))
        player = cursor.fetchone()
        if not player:
            return f"Player {player_name} not found or already drafted"

        # Make the pick
        cursor.execute("""
            INSERT INTO draft_picks (year, pick, team, player_name, position)
            VALUES (2024, ?, ?, ?, ?)
        """, (pick_no, team_name, player[0], player[1]))
        
        # Remove from available players
        cursor.execute("DELETE FROM available_players WHERE LOWER(name) LIKE ?",
                      ('%' + player_name.lower() + '%',))
        
        # Update draft order
        cursor.execute("DELETE FROM draft_order WHERE [Pick No.] = ?", (pick_no,))
        
        conn.commit()
        return f"{team_name} has selected {player[0]} ({player[1]}) with pick #{pick_no}"

    except Exception as e:
        return f"Error making draft pick: {e}"
    finally:
        if conn:
            conn.close()