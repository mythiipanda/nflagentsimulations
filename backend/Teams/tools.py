import os
import sqlite3
from typing import List, Tuple, Optional
import logging
TEAM_MAPPINGS = {
    # Canonical form (key) to display form (value)
    'arizona-cardinals': 'Arizona Cardinals',
    'atlanta-falcons': 'Atlanta Falcons',
    'baltimore-ravens': 'Baltimore Ravens',
    'buffalo-bills': 'Buffalo Bills',
    'carolina-panthers': 'Carolina Panthers',
    'chicago-bears': 'Chicago Bears',
    'cincinnati-bengals': 'Cincinnati Bengals',
    'cleveland-browns': 'Cleveland Browns',
    'dallas-cowboys': 'Dallas Cowboys',
    'denver-broncos': 'Denver Broncos',
    'detroit-lions': 'Detroit Lions',
    'green-bay-packers': 'Green Bay Packers',
    'houston-texans': 'Houston Texans',
    'indianapolis-colts': 'Indianapolis Colts',
    'jacksonville-jaguars': 'Jacksonville Jaguars',
    'kansas-city-chiefs': 'Kansas City Chiefs',
    'las-vegas-raiders': 'Las Vegas Raiders',
    'los-angeles-chargers': 'Los Angeles Chargers',
    'los-angeles-rams': 'Los Angeles Rams',
    'miami-dolphins': 'Miami Dolphins',
    'minnesota-vikings': 'Minnesota Vikings',
    'new-england-patriots': 'New England Patriots',
    'new-orleans-saints': 'New Orleans Saints',
    'new-york-giants': 'New York Giants',
    'new-york-jets': 'New York Jets',
    'philadelphia-eagles': 'Philadelphia Eagles',
    'pittsburgh-steelers': 'Pittsburgh Steelers',
    'san-francisco-49ers': 'San Francisco 49ers',
    'seattle-seahawks': 'Seattle Seahawks',
    'tampa-bay-buccaneers': 'Tampa Bay Buccaneers',
    'tennessee-titans': 'Tennessee Titans',
    'washington-commanders': 'Washington Commanders'
}

# Mapping from roster positions to PFF data positions
POSITION_MAPPINGS = {
    'QB': 'QB',
    'RB': 'HB',
    'WR': 'WR',
    'TE': 'TE',
    'LT': 'T',
    'LG': 'G',
    'C' : 'C',
    'RG': 'G',
    'RT': 'T',
    'OL': 'T', # Defaulting to T, needs more specific handling if needed
    'FB': 'HB',
    'T': 'T',
    'G': 'G',
    'DE': 'ED',
    'DT': 'DI',
    'NT': 'DI',
    'LB': 'LB',
    'ILB': 'LB',
    'OLB': 'LB',
    'EDGE' : 'ED',
    'CB': 'CB',
    'S': 'S',
    'FS': 'S',
    'SS': 'S',
    'K': 'K',
    'P': 'P',
    'LS': 'LS',
    'DL': 'DI', # Assuming DL maps to Defensive Interior as a general term
    'DB': 'S'  # Assuming DB maps to Safety as a general term
}

def normalize_team_name(team_name: str, for_display: bool = False) -> str:
    """
    Normalizes team names between filesystem format and display format.
    """
    canonical = team_name.lower().replace(' ', '-')
    if canonical not in TEAM_MAPPINGS:
        for k, v in TEAM_MAPPINGS.items():
            if v.lower() == team_name.lower():
                canonical = k
                break
        else:
            raise ValueError(f"Invalid team name: {team_name}")
    logging.info(f"Normalized team name: {team_name} -> {canonical}")
    return TEAM_MAPPINGS[canonical] if for_display else canonical

def get_team_roster(team_name: str, team_db_path: Optional[str] = None) -> str:
    """Retrieves the current roster for a given team."""
    conn = None
    try:
        normalized_name = normalize_team_name(team_name, for_display=False)
        if not team_db_path:
            team_db_path = f"{normalized_name}/team_data.db"

        if not os.path.exists(team_db_path):
            return f"Error: Database not found for {team_name}"

        conn = sqlite3.connect(team_db_path)
        cursor = conn.cursor()
        roster = []

        cursor.execute(f"SELECT full_name, position, jersey_number FROM 'roster'")
        roster.extend(cursor.fetchall())

        formatted_roster = [f"{player[0]} (#{player[2]}) - {player[1]}" for player in roster]
        logging.info("Roster for %s: %s", team_name, formatted_roster)
        return f"Roster for {normalize_team_name(team_name, for_display=True)}:\n" + "\n".join(formatted_roster)

    except Exception as e:
        return f"Error retrieving roster: {e}"
    finally:
        if conn:
            conn.close()

def get_player_stats(player_name: str, team_db_path: Optional[str] = None) -> str:
    conn = None
    try:
        if not team_db_path or not os.path.exists(team_db_path):
            return "Error: Team database not found"

        conn = sqlite3.connect(team_db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT position FROM roster WHERE LOWER(full_name) LIKE LOWER(?)", (f"%{player_name}%",))
        player_info = cursor.fetchone()
        if not player_info:
            return f"Player {player_name} not found in the roster."
        roster_position = player_info[0]
        pff_position = POSITION_MAPPINGS.get(roster_position)
        if not pff_position:
            return f"Error: No PFF position mapping found for roster position '{roster_position}'."

        table_map = {'QB': 'offense', 'HB': 'offense', 'WR': 'offense', 'TE': 'offense',
                     'T': 'offense', 'G': 'offense', 'C': 'offense',
                     'ED': 'defense', 'DI': 'defense', 'LB': 'defense',
                     'CB': 'defense', 'S': 'defense',
                     'K': 'special_teams', 'P': 'special_teams', 'LS': 'special_teams'}

        found_stats = False
        for pff_pos, table_name in table_map.items():
            if pff_pos == pff_position:
                cursor.execute(f"PRAGMA table_info('{table_name}')")
                columns_info = cursor.fetchall()
                columns = [info[1] for info in columns_info]

                select_cols = [col for col in ['Player', 'JerseyNumber', 'Position', 'GamesPlayed',
                                               f'{table_name.capitalize()}OverallGrade', f'{table_name.capitalize()}TotalSnaps'] if col in columns]

                cursor.execute(f"SELECT {', '.join(select_cols)} FROM '{table_name}' WHERE LOWER(Player) LIKE LOWER(?) AND Position = ?", (f"%{player_name}%", pff_position))
                stats = cursor.fetchone()

                if stats:
                    found_stats = True
                    stat_map = dict(zip(select_cols, stats))
                    return "\n".join([f"{key.replace('Offense', '').replace('Defense', '').replace('Special_teams', '').replace('Overall', 'Overall ')}: {value}" for key, value in stat_map.items()])
                break

        if not found_stats:
            return f"Player {player_name} found on the roster, but no stats available for PFF position '{pff_position}'."

        return "Error retrieving player stats (internal logic issue)"

    except Exception as e:
        return f"Error retrieving player stats: {e}"
    finally:
        if conn:
            conn.close()
def get_draft_order(db_path: Optional[str] = None) -> str:
    """Retrieves the current draft order."""
    conn = None
    try:
        if not db_path or not os.path.exists(db_path):
            return "Error: Draft database not found"

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT [Pick No.], Team FROM draft_order ORDER BY [Pick No.]")
        picks = cursor.fetchall()

        if not picks:
            return "No draft order found"

        formatted_picks = [f"Pick {pick[0]}: {pick[1]}" for pick in picks]
        logging.info("Draft order: %s", formatted_picks)
        return "Current draft order:\n" + "\n".join(formatted_picks)

    except Exception as e:
        return f"Error retrieving draft order: {e}"
    finally:
        if conn:
            conn.close()

def get_remaining_needs(team_name: str, team_db_path: Optional[str] = None) -> str:
    """Analyzes a team's roster and identifies positional needs."""
    conn = None
    try:
        normalized_name = normalize_team_name(team_name, for_display=False)
        if not team_db_path:
            team_db_path = f"{normalized_name}/team_data.db"

        if not os.path.exists(team_db_path):
            return f"Error: Team database not found for {team_name}"

        conn = sqlite3.connect(team_db_path)
        cursor = conn.cursor()

        position_counts = {}
        for table in ['offense', 'defense', 'special-teams']:
            cursor.execute(f"SELECT Position, COUNT(*) FROM '{table}' GROUP BY Position")
            for position, count in cursor.fetchall():
                position_counts[position] = position_counts.get(position, 0) + count

        # Define position thresholds
        needs = []
        thresholds = {
            'QB': 3, 'RB': 4, 'WR': 6, 'TE': 3, 'T': 8, 'G': 8, 'C': 8,
            'DI': 6, 'ED': 4, 'LB': 6, 'CB': 6, 'S': 4,
            'K': 1, 'P': 1, 'LS': 1
        }

        for position, threshold in thresholds.items():
            current = position_counts.get(position, 0)
            if current < threshold:
                needs.append(f"{position}: Have {current}, Need {threshold-current} more")

        display_name = normalize_team_name(team_name, for_display=True)
        logging.info("Roster needs for %s: %s", team_name, needs)
        return f"Roster needs for {display_name}:\n" + "\n".join(needs)

    except Exception as e:
        return f"Error analyzing team needs: {e}"
    finally:
        if conn:
            conn.close()

def make_draft_pick(team_name: str, player_name: str, db_path: Optional[str] = None, team_db_path: Optional[str] = None) -> str:
    """Makes a draft pick."""
    conn = None
    try:
        if not db_path or not os.path.exists(db_path):
            return "Error: Draft database not found"

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Use display format for draft DB queries
        draft_team_name = normalize_team_name(team_name, for_display=True)

        cursor.execute("SELECT [Pick No.], Team FROM draft_order ORDER BY [Pick No.] LIMIT 1")
        result = cursor.fetchone()
        if not result:
            return "No more picks available in draft order"

        pick_no, current_team = result
        if current_team != draft_team_name:
            return f"It is not {draft_team_name}'s turn to pick. Current pick belongs to {current_team}"

        # Make the pick
        cursor.execute("""
            INSERT INTO picks ([Pick No.], Team, Player)
            VALUES (?, ?, ?)
        """, (pick_no, draft_team_name, player_name))

        # Remove the used pick
        cursor.execute("DELETE FROM draft_order WHERE [Pick No.] = ?", (pick_no,))

        conn.commit()
        logging.info("%s selects %s with pick #%d", draft_team_name, player_name, pick_no)
        return f"{draft_team_name} selects {player_name} with pick #{pick_no}"

    except Exception as e:
        return f"Error making draft pick: {e}"
    finally:
        if conn:
            conn.close()

def get_ranked_players(team_name: str, team_db_path: Optional[str] = None) -> str:
    """
    Retrieves and ranks players by position based on overall grade.
    Now uses POSITION_MAPPINGS to find the correct PFF table and handles different roster positions mapping to the same PFF position.
    """
    conn = None
    try:
        normalized_name = normalize_team_name(team_name, for_display=False)
        if not team_db_path:
            team_db_path = f"{normalized_name}/team_data.db"

        if not os.path.exists(team_db_path):
            return f"Error: Database not found for {team_name}"

        conn = sqlite3.connect(team_db_path)
        cursor = conn.cursor()

        # Get the roster
        cursor.execute("SELECT full_name, position, jersey_number FROM roster")
        roster = cursor.fetchall()

        # Dictionary to hold players by PFF position
        players_by_pff_position = {}
        for player_name, roster_position, jersey_number in roster:
            pff_position = POSITION_MAPPINGS.get(roster_position)
            if not pff_position:
                print(f"Warning: No PFF position mapping found for roster position '{roster_position}'. Skipping player {player_name}.")
                continue
            if pff_position not in players_by_pff_position:
                players_by_pff_position[pff_position] = []
            players_by_pff_position[pff_position].append((player_name, roster_position, jersey_number))

        # Dictionary to hold ranked players
        ranked_players = {}

        # Define the tables and their corresponding PFF positions
        tables_and_positions = {
            'offense': ['QB', 'HB', 'WR', 'TE', 'T', 'G', 'C'],
            'defense': ['ED', 'DI', 'LB', 'CB', 'S'],
            'special_teams': ['K', 'P', 'LS']
        }

        # Fetch and rank players for each PFF position
        for pff_position, players in players_by_pff_position.items():
            # Determine the relevant table based on PFF position
            relevant_table = None
            for table, positions in tables_and_positions.items():
                if pff_position in positions:
                    relevant_table = table
                    break

            if not relevant_table:
                # Handle PFF positions not found in any table
                print(f"Warning: No table found for PFF position '{pff_position}'. Skipping.")
                continue

            player_stats = []
            for player_name, roster_position, jersey_number in players:
                # Fetch stats from the relevant table
                if relevant_table == 'offense':
                    columns_to_select = ['Player', 'JerseyNumber', 'OffenseOverallGrade', 'Position']
                elif relevant_table == 'defense':
                    columns_to_select = ['Player', 'JerseyNumber', 'DefenseOverallGrade', 'Position']
                elif relevant_table == 'special-teams':
                    columns_to_select = ['Player', 'JerseyNumber', 'SpecialTeamsOverallGrade', 'Position']
                else:
                    continue  # Skip if no relevant table

                cursor.execute(f"""
                    SELECT {', '.join(columns_to_select)}
                    FROM '{relevant_table}'
                    WHERE LOWER(Player) LIKE LOWER(?) AND Position = ?
                """, (f"%{player_name}%", pff_position))

                result = cursor.fetchone()

                if result:
                    player, jersey_number, grade, pos = result
                    try:
                        grade = float(grade)
                    except ValueError:
                        grade = 0.0  # Default grade if conversion fails
                    player_stats.append((player_name, grade, jersey_number, roster_position))  # Include roster position

            # Sort players by grade in descending order
            player_stats.sort(key=lambda x: x[1], reverse=True)
            ranked_players[pff_position] = player_stats

        # Format the output
        output = ""
        for pff_position, players in ranked_players.items():
            output += f"{pff_position}:\n"
            for i, (player_name, grade, jersey_number, roster_position) in enumerate(players):
                output += f"{i+1}. {player_name} (#{jersey_number} - {roster_position}) - {grade}\n"  # Show roster position
            output += "\n"
        logging.info("Ranked players for %s: %s", team_name, output)
        return output.strip()

    except Exception as e:
        return f"Error ranking players: {e}"
    finally:
        if conn:
            conn.close()

def get_position_stats(team_name: str, position: str, team_db_path: Optional[str] = None) -> str:
    """
    Gets stats for all players in a position group and ranks them.
    Includes Jersey Number, Overall Grade, and Total Snaps in the output.
    Uses PFF position for lookup.
    """
    conn = None
    try:
        normalized_name = normalize_team_name(team_name, for_display=False)
        if not team_db_path:
            team_db_path = f"{normalized_name}/team_data.db"

        if not os.path.exists(team_db_path):
            return f"Error: Database not found for {team_name}"

        conn = sqlite3.connect(team_db_path)
        cursor = conn.cursor()

        pff_position = POSITION_MAPPINGS.get(position)
        if not pff_position:
            return f"Error: No PFF position mapping found for roster position '{position}'."

        # Determine which table to query based on PFF position
        tables_and_positions = {
            'offense': ['QB', 'HB', 'WR', 'TE', 'T', 'G', 'C'],
            'defense': ['ED', 'DI', 'LB', 'CB', 'S'],
            'special_teams': ['K', 'P', 'LS']
        }
        relevant_table = None
        for table, positions in tables_and_positions.items():
            if pff_position in positions:
                relevant_table = table
                break

        if not relevant_table:
            return f"Error: Invalid position '{position}'"

        # Define columns to select based on the table
        if relevant_table == 'offense':
            columns_to_select = ['Player', 'JerseyNumber', 'OffenseOverallGrade', 'OffenseTotalSnaps']
        elif relevant_table == 'defense':
            columns_to_select = ['Player', 'JerseyNumber', 'DefenseOverallGrade', 'DefenseTotalSnaps']
        elif relevant_table == 'special-teams':
            columns_to_select = ['Player', 'JerseyNumber', 'SpecialTeamsOverallGrade', 'SpecialTeamsTotalSnaps']
        else:
            return f"Error: Could not determine table for PFF position '{pff_position}'"

        # Fetch and rank players from the relevant table
        cursor.execute(f"""
            SELECT {', '.join(columns_to_select)}
            FROM '{relevant_table}'
            WHERE Position = ? AND LOWER(Team) = LOWER(?)
            ORDER BY {columns_to_select[2]} DESC
        """, (pff_position, normalized_name))

        players = cursor.fetchall()

        if not players:
            return f"No players found for position '{position}' on team '{team_name}'"

        # Format the output
        ranking = f"{position} Rankings for {normalize_team_name(team_name, for_display=True)}:\n"
        for idx, player_data in enumerate(players, start=1):
            name, number, grade, snaps = player_data
            ranking += f"{idx}. {name} (#{number}) - Grade: {grade}, Snaps: {snaps}\n"
        logging.info("Position stats for %s (%s): %s", team_name, position, ranking)
        return ranking.strip()

    except Exception as e:
        return f"Error getting position stats: {e}"
    finally:
        if conn:
            conn.close()

def compare_players(player1_name: str, player2_name: str, team_db_path: Optional[str] = None) -> str:
    """
    Compares the stats of two players side-by-side.
    """
    player1_stats_str = get_player_stats(player1_name, team_db_path=team_db_path)
    player2_stats_str = get_player_stats(player2_name, team_db_path=team_db_path)

    # Check for errors in fetching stats
    if player1_stats_str.startswith("Error"):
        return player1_stats_str
    if player2_stats_str.startswith("Error"):
        return player2_stats_str

    # Parse the stats
    player1_stats = {}
    for line in player1_stats_str.split("\n"):
        if line.strip() and ":" in line:
            key, value = line.split(":", 1)
            player1_stats[key.strip()] = value.strip()

    player2_stats = {}
    for line in player2_stats_str.split("\n"):
        if line.strip() and ":" in line:
            key, value = line.split(":", 1)
            player2_stats[key.strip()] = value.strip()

    # Format the comparison
    comparison = f"{player1_name} vs {player2_name}\n\n"
    comparison += f"{'Stat':<20}{player1_name:<30}{player2_name:<30}\n"
    comparison += f"{'-'*70}\n"

    for stat in ["Jersey Number", "Position", "Games Played", "Overall Grade", "Total Snaps"]:
        stat_key = stat if stat in player1_stats else stat.replace(" ", "")
        comparison += f"{stat:<20}{player1_stats.get(stat_key, 'N/A'):<30}{player2_stats.get(stat_key, 'N/A'):<30}\n"
    logging.info("Player comparison: %s", comparison)
    return comparison

def get_position_group(team_name: str, position: str, team_db_path: Optional[str] = None) -> str:
    """
    Gets all players of a specific position on a team, compares their stats, and ranks them.
    Uses PFF position for lookup.
    """
    conn = None
    try:
        if not team_db_path or not os.path.exists(team_db_path):
            return "Error: Team database not found"

        conn = sqlite3.connect(team_db_path)
        cursor = conn.cursor()

        pff_position = POSITION_MAPPINGS.get(position)
        if not pff_position:
            return f"Error: No PFF position mapping found for roster position '{position}'."

        # Get the roster to identify all players of the specified mapped PFF position
        cursor.execute("SELECT full_name, position FROM roster")
        roster = cursor.fetchall()

        players_of_position = [full_name for full_name, roster_pos in roster if POSITION_MAPPINGS.get(roster_pos) == pff_position]

        if not players_of_position:
            return f"No players found for position '{position}' on team '{team_name}'"

        # Get stats for each player and store them in a list of dictionaries
        player_stats_list = []
        for player_name in players_of_position:
            stats_str = get_player_stats(player_name, team_db_path=team_db_path)

            # Check for errors in fetching stats
            if stats_str.startswith("Error"):
                print(f"Error fetching stats for {player_name}: {stats_str}")
                continue

            player_stats = {}
            for line in stats_str.split("\n"):
                if line.strip() and ":" in line:
                    key, value = line.split(":", 1)
                    player_stats[key.strip()] = value.strip()

            if not all(key in player_stats for key in ["Jersey Number", "Overall Grade", "Total Snaps"]):
                print(f"Warning: Missing keys in player stats for {player_name}: {player_stats}")
                continue
            player_stats_list.append(player_stats)

        # Sort players by Overall Grade in descending order
        player_stats_list.sort(key=lambda x: float(x.get("Overall Grade", 0)), reverse=True)

        # Format the output
        output = f"{position} Rankings for {team_name}:\n\n"
        output += f"{'Rank':<5}{'Player':<30}{'Jersey':<8}{'Grade':<8}{'Snaps':<8}\n"
        output += "-" * 60 + "\n"

        for i, stats in enumerate(player_stats_list):
            output += f"{i+1:<5}{stats.get('Player', 'N/A'):<30}{stats.get('Jersey Number', 'N/A'):<8}{stats.get('Overall Grade', 'N/A'):<8}{stats.get('Total Snaps', 'N/A'):<8}\n"
        logging.info("Position group stats for %s (%s): %s", team_name, position, output)
        return output

    except Exception as e:
        return f"Error getting position group stats: {e}"
    finally:
        if conn:
            conn.close()