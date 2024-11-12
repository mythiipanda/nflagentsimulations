from crew_test import NflCrew  # Import NflCrew
nfl_crew = NflCrew()
inputs = {"query": "Test query"}
response = nfl_crew.crew().kickoff(inputs=inputs)
print("Response from kickoff:", response)  # Print the response