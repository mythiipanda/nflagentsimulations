from crewai.flow.flow import Flow, listen, start
from typing import List
import logging
from src.nfl_draft_sim.crews.orchestrator.orchestrator_crew import NflDraftOrchestrator
from src.nfl_draft_sim.crews.TEMPLATE.team_crew import NflTeamCrew
from src.nfl_draft_sim.flows.team_communication_flow import TeamCommunicationFlow, TeamTradeFlow
from dotenv import load_dotenv
import os

load_dotenv()

logging.basicConfig(level=logging.DEBUG)

class NflDraftFlow(Flow):
    def __init__(self, teams: List[str]):
        self.teams = teams
        self.orchestrator = NflDraftOrchestrator(teams)
        self.team_crews = {team: NflTeamCrew(team, self.orchestrator) for team in teams}
        self.team_communication_flows = {
            team: TeamCommunicationFlow(team, self.orchestrator) for team in teams
         }
        self.trade_flows = {} # trade flows will be created as necessary

    @start()
    def initiate_draft(self):
        logging.info("Initiating NFL draft simulation...")
        # Initiate orchestrator to setup env and get data
        self.orchestrator.orchestrator_crew().kickoff(inputs={"message": "Starting the NFL Draft Process"})
        return {"message":"Draft Started"}

    @listen(initiate_draft)
    def process_draft_rounds(self, initiator_output):
      for pick_number in range(len(self.teams)):
            # Simulate the draft process for each pick
          logging.info(f"Processing round {pick_number+1}")
          for team in self.teams:
                logging.info(f"Team {team} is making pick {pick_number + 1}")
                team_crew = self.team_crews[team]
                team_communication_flow = self.team_communication_flows[team]
                team_crew_results = team_communication_flow.kickoff()
                team_crew.team_crew().kickoff(inputs={"team_name": team, "pick_number": pick_number + 1})

                # Update the universal database with the pick
                pick = {"team": team, "pick_number": pick_number + 1, "player": team_crew.select_pick_task().output}
                self.orchestrator.database.add_pick(team, pick)
                # This should be called by agents instead, so teams can propose trades at any time
                #   trade_flow = TeamTradeFlow(from_team=team, to_team= self.teams[pick_number%len(self.teams)], orchestrator=self.orchestrator )
                #   trade_results = trade_flow.kickoff()
                #   self.orchestrator.database.add_trade(trade_results)
                
      return {"message":"Draft Completed"}
