## How We Built It
The project is being developed using the following technologies:

- **Frontend**: ReactJS for a dynamic and responsive user interface.
- **Backend**: Initially, we used a NodeJS server, but we transitioned to Flask due to its flexibility and ability to integrate with multi-agentic frameworks such as **CrewAI**, **Autogen**, and others.
- **Database**: MongoDB to store and manage our data.


## What's Coming?
We are in the early stages of this project, having started just two weeks ago. Our roadmap includes:

- **Draft Prediction Model**: Developing a model to predict draft outcomes based on team needs, player statistics, and other relevant data.
- **Draft Simulation**: Allowing users to simulate draft scenarios and explore different outcomes.

### Planned Features:
- **RAG/GraphRAG Integration**: We plan to integrate RAG and/or GraphRAG to fetch and display the latest articles, injury reports, team summaries, and other critical information.
- **CrewAI/Autogen**: Implementing a multi-agentic framework that will conduct research on NFL teams, generate specific team analyses, and provide detailed charts and insights.
- **All-in-One Dashboard**: We are working on an enhanced dashboard that will provide users with an in-depth, functional overview of player statistics and team data.
# TODO/NOTES:
- Speculative RAG (generalist + specialist for faster responses)
- look into https://github.com/groq/groq-api-cookbook/blob/main/tutorials/crewai-mixture-of-agents/Mixture-of-Agents-Crew-AI-Groq.ipynb
- mixture of agents
- integrate multiple llms (parallel)?
- structured outputs
- Parsers: llamaparse, firecrawl
- Notes: check only relevant documents, use web api to double check on documents agents are unsure on
- GraphRAG?
- verification with datasets -> teams
- more tools
- early stopping
## Stay Tuned!

