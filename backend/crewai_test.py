import os
from crewai import Agent, Task, Crew, Process
from dotenv import load_dotenv
from langchain_community.tools import DuckDuckGoSearchRun
from crewai import LLM
from langchain_openai import ChatOpenAI
from crewai_tools import WebsiteSearchTool
load_dotenv()

# Configure the WebsiteSearchTool with Cerebras LLM and Hugging Face embeddings
tool = WebsiteSearchTool(
    config=dict(
        llm=dict(
            provider="openai",  # Use 'openai' as the provider for compatibility
            config=dict(
                api_key=os.getenv("CEREBRAS_API_KEY"),
                model="llama3.1-70b",  # Replace with your Cerebras model name
                base_url="https://api.cerebras.ai/v1",  # Point to Cerebras API
                temperature=0.5,
                top_p=0.9,
                stream=False,
            ),
        ),
        embedder=dict(
            provider="huggingface",  # Use free embeddings from Hugging Face
            config=dict(
                model="sentence-transformers/all-MiniLM-L6-v2"
            ),
        ),
    )
)

manager = Agent(
    role="Project Manager",
    goal="Understand the prompt and efficiently manage the crew and ensure high-quality task completion",
    backstory="You're an experienced project manager, skilled in overseeing complex projects and guiding teams to success. Your role is to coordinate the efforts of the crew members, ensuring that each task is completed on time and to the highest standard.",
    allow_delegation=True,
)
# Initialize tools and LLM
search_tool = DuckDuckGoSearchRun()
llm = LLM(
    api_key=os.getenv("CEREBRAS_API_KEY"),
    base_url="https://api.cerebras.ai/v1",
    model="cerebras/llama3.1-8b"
)

# Enhanced Agents
lead_analyst = Agent(
    role='Lead NFL Analyst',
    goal='Coordinate research efforts and synthesize insights from multiple data sources to provide comprehensive NFL analysis',
    memory=True,
    tools=[search_tool, tool],
    backstory="You are a veteran NFL analyst with 15+ years of experience in statistical analysis and player evaluation. "
              "Your expertise spans game film analysis, advanced metrics, and historical trends.",
    llm=llm,
    max_rpm=1,
    max_iter=1
)

stats_analyst = Agent(
    role='Statistical Analyst',
    goal='Process and analyze NFL statistical data to identify trends, patterns, and significant insights',
    memory=True,
    tools=[search_tool, tool],
    backstory="Former data scientist specialized in sports analytics, with deep knowledge of advanced NFL metrics "
              "including DVOA, EPA, and custom performance indicators.",
    llm=llm,
    max_rpm=1,
    max_iter=1
)

player_scout = Agent(
    role='Player Scout',
    goal='Evaluate player performances, analyze matchups, and provide detailed scouting reports',
    memory=True,
    tools=[search_tool, tool],
    backstory="Ex-NFL scout with expertise in player evaluation, film study, and talent assessment. "
              "Specialized in identifying key performance indicators and future potential.",
    llm=llm,
    max_rpm=1,
    max_iter=1
)

# Enhanced Tasks
data_collection_task = Task(
    description="Gather comprehensive NFL statistics, including advanced metrics, player performance data, and historical trends",
    expected_output="Structured dataset containing relevant NFL statistics and metrics",
    agent=stats_analyst
)

scouting_analysis_task = Task(
    description="Analyze player performances, evaluate matchups, and generate detailed scouting reports",
    expected_output="Detailed player analysis and scouting insights",
    agent=player_scout
)

synthesis_task = Task(
    description="Synthesize statistical analysis and scouting reports into comprehensive insights",
    expected_output="Cohesive analysis combining statistical and scouting perspectives",
    agent=lead_analyst
)

# Assemble enhanced crew
crew = Crew(
    agents=[lead_analyst, stats_analyst, player_scout],
    tasks=[data_collection_task, scouting_analysis_task, synthesis_task],
    process=Process.hierarchical,
    verbose=True,
    planning=True,
    manager_agent=manager,
    planning_llm=ChatOpenAI(
            openai_api_key=os.getenv("CEREBRAS_API_KEY"),
            base_url="https://api.cerebras.ai/v1",
            model_name="cerebras/llama3.1-8b",
            temperature=0.7
        )
    )


def run_nfl_analysis(query):
    try:
        print(f"Initiating NFL analysis for query: {query}")
        result = crew.kickoff(inputs={'query': query})
        return result
    except Exception as e:
        print(f"Error during analysis: {str(e)}")
        return None

# Example usage
if __name__ == "__main__":
    result = run_nfl_analysis("Analyze the top 10 NFL quarterbacks for 2024 in terms of passer rating, completion percentage, and scouting evaluation.")
    print("\nAnalysis Results:")
    print(result)