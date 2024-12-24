## Core Framework
- Language: Python
- Agent Model: Custom ReAct implementation
- LLM: Cerebras Cloud SDK (using `llama3.1-8b` model for chat completions)

## Data Management
- Database: SQLite
- Database Files: `nfl_draft.db`, `team_data.db` (per team)

## Dependencies
- `cerebras_cloud_sdk`: For Cerebras API access
- `python-dotenv`: For environment variable management