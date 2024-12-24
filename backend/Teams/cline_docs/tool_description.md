## Tool Descriptions

This document describes the functionality of each tool available in `tools.py`.

### `get_team_roster(team_name)`

Retrieves the roster for a given team from the team's database.

**Args:**

*   `team_name` (str): The name of the team (e.g., "arizona-cardinals").

**Returns:**

*   str: A string representation of the team's roster. If the database is not found or an error occurs, returns an appropriate error message.

### `get_player_stats(player_name)`

Retrieves stats for a given player from the `available_players` table in the `nfl_draft.db` database.

**Args:**

*   `player_name` (str): The name of the player.

**Returns:**

*   str: A string representation of the player's stats. If the player is not found or an error occurs, returns an appropriate error message.

### `get_draft_order()`

Retrieves the current draft order from the `draft_order` table in the `nfl_draft.db` database.

**Returns:**

*   str: A string representation of the draft order. If an error occurs, returns an appropriate error message.

### `get_remaining_needs(team_name)`

**Placeholder:** This function is intended to analyze a team's roster and identify positional needs. The logic for determining needs is not yet implemented.

**Args:**

*   `team_name` (str): The name of the team.

**Returns:**

*   str: A placeholder string indicating the remaining needs for the team.

### `make_draft_pick(team_name, player_name)`

Simulates making a draft pick by updating the `draft_picks` and `available_players` tables in the `nfl_draft.db` database.

**Args:**

*   `team_name` (str): The name of the team making the pick.
    *   `player_name` (str): The name of the player being drafted.

**Returns:**

*   str: A confirmation message indicating the successful pick. If an error occurs, returns an appropriate error message.