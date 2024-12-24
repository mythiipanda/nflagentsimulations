## Key Components
- `agent.py`: Contains the core Agent class definition, including the ReAct loop implementation. Now uses the Cerebras API.
- `tools.py`: Houses functions that agents can utilize (database queries for roster, player stats, draft order, making picks).
- `orchestrator.py`: Defines the Orchestrator agent for managing the draft.
- `main.py`: Entry point for running the simulation.
- `test_agent_tools.py`: Contains unit tests for the Agent class and tools.

## Data Flow
1. Orchestrator initializes the draft.
2. Agents use tools to access data and make decisions.
3. Agent actions update the draft state (database).
4. Orchestrator monitors the draft and triggers agent actions.

## External Dependencies
- `nfl_draft.db`: SQLite database with player and draft information.
- `team_data.db`: SQLite databases (per team) with roster data.
- `cerebras_cloud_sdk`: Python SDK for interacting with the Cerebras API.

## Recent Significant Changes
- [x] Created initial `agent.py` with basic Agent class structure.
- [x] Implemented `_react_loop`, `generate_thought`, `choose_action`, `execute_action` in `agent.py`.
- [x] Created `tools.py` and implemented initial database interaction tools.
- [x] Added `test_agent_tools.py` with basic unit tests.
- [x] Implemented rate limiting using a decorator in `rate_limiter.py` and integrated it into `agent.py`.
- [x] Removed `rate_limiter.py` and related code as rate limiting is no longer needed.
- [x] Adapted `agent.py` to use the Cerebras API instead of the Gemini API.
- [x] Removed Gemini-specific code and updated prompt formatting for Cerebras.

## User Feedback Integration
- N/A (No user feedback integrated yet)