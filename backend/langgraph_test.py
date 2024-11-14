# NFL Analysis using LangGraph
import os
import functools
from typing import TypedDict, Annotated, List, Union
import operator
from dotenv import load_dotenv

from langchain_core.agents import AgentAction, AgentFinish
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langgraph.graph import END, StateGraph, START

# Load environment variables
load_dotenv()

# Define graph state
class AgentState(TypedDict):
    input: str  # User's query
    chat_history: list[BaseMessage]  # Conversation history
    intermediate_steps: Annotated[list[tuple[AgentAction, str]], operator.add]  # Agent actions

# Custom tools
@tool("stats_search")
def stats_search(query: str):
    """Search NFL statistics and data."""
    # Implement ChromaDB search here
    return "NFL stats results"

@tool("team_analysis") 
def team_analysis(team: str):
    """Analyze NFL team performance."""
    return "Team analysis results"

@tool("player_research")
def player_research(player: str):
    """Research NFL player information."""
    return "Player research results"

@tool("write_report")
def write_report(content: dict):
    """Write final analysis report."""
    return f"""
    Research Report
    --------------
    {content['introduction']}
    
    Analysis
    --------
    {content['analysis']}
    
    Conclusions
    -----------
    {content['conclusions']}
    """

# Create Oracle/Router
system_prompt = """You are an NFL analysis coordinator.
Route queries to appropriate specialists:
- Researcher: For general NFL research and data gathering
- Stats Analyst: For statistical analysis and metrics
- Game Analyst: For game strategy and performance analysis
- Writer: For final report compilation"""

prompt = ChatPromptTemplate.from_messages([
    ("system", system_prompt),
    MessagesPlaceholder(variable_name="chat_history"),
    ("user", "{input}"),
    ("assistant", "Current progress: {intermediate_steps}")
])

# Initialize LLM
from langchain_cerebras import ChatCerebras
from dotenv import load_dotenv
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")
llm = ChatCerebras(api_key=openai_api_key, model="llama3.1-8b", temperature=0.7)

# Define tools
tools = [stats_search, team_analysis, player_research, write_report]

# Create agents
def create_agent(name: str, tools: list, role: str):
    """Create specialized NFL analysis agent."""
    prompt = ChatPromptTemplate.from_messages([
        ("system", f"You are an NFL {role}. {role}-specific instructions here."),
        MessagesPlaceholder(variable_name="chat_history"),
        ("user", "{input}"),
    ])
    return prompt | llm.bind_tools(tools)

# Agent nodes
agents = {
    "researcher": create_agent("Researcher", [stats_search, player_research], "Research Specialist"),
    "stats_analyst": create_agent("StatsAnalyst", [stats_search, team_analysis], "Statistical Analyst"),
    "game_analyst": create_agent("GameAnalyst", [team_analysis, player_research], "Game Analyst"),
    "writer": create_agent("Writer", [write_report], "Content Writer")
}

# Node execution
def agent_node(state: AgentState, agent, name: str):
    """Execute agent node."""
    result = agent.invoke(state)
    return {
        "intermediate_steps": [(
            AgentAction(tool=name, tool_input=state["input"], log=str(result)),
            result
        )]
    }

# Router logic
def router(state: AgentState):
    """Route between agents based on current state."""
    last_step = state["intermediate_steps"][-1] if state["intermediate_steps"] else None
    if not last_step:
        return "researcher"
    if "FINAL" in str(last_step):
        return END
    # Add routing logic based on agent outputs
    return "writer"

# Build graph
workflow = StateGraph(AgentState)

# Add nodes
for name, agent in agents.items():
    workflow.add_node(name, functools.partial(agent_node, agent=agent, name=name))

# Add edges
workflow.add_conditional_edges(
    "researcher",
    router,
    {
        "stats_analyst": "stats_analyst",
        "game_analyst": "game_analyst",
        "writer": "writer",
        END: END
    }
)

workflow.add_conditional_edges(
    "stats_analyst",
    router,
    {
        "game_analyst": "game_analyst", 
        "writer": "writer",
        END: END
    }
)

workflow.add_edge("writer", END)
workflow.add_edge(START, "researcher")

# Compile graph
graph = workflow.compile()

# Example usage
if __name__ == "__main__":
    result = graph.invoke({
        "input": "Analyze the performance of NFL quarterbacks this season",
        "chat_history": [],
        "intermediate_steps": []
    })
    print(result)