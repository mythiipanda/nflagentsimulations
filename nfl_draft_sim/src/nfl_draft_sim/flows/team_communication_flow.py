from crewai.flow.flow import Flow, listen, start
from typing import List
import logging

logging.basicConfig(level=logging.DEBUG)

class TeamCommunicationFlow(Flow):
  """Handles communication between team crews and the orchestrator, including reporting results and
  coordinating any necessary actions related to the draft."""

  def __init__(self, team_name, orchestrator):
    self.team_name = team_name
    self.orchestrator = orchestrator

  @start()
  def announce_start(self):
    logging.info(f"Team {self.team_name} started their draft process.")
    return {"message": f"Team {self.team_name} is starting their draft process"}
  
  @listen(announce_start)
  def report_results(self, output):
    # Report back to the orchestrator, add information to the database
     logging.info(f"Team {self.team_name} is reporting back on their process")
     # self.orchestrator.add_pick(self.team_name, output)
     return {"message": f"Team {self.team_name} is reporting their process results"}

class TeamTradeFlow(Flow):
   """Manages the trade proposal from a specific team to another."""

   def __init__(self, from_team, to_team, orchestrator):
        self.from_team = from_team
        self.to_team = to_team
        self.orchestrator = orchestrator

   @start()
   def create_trade_proposal(self):
        logging.info(f"Team {self.from_team} is proposing a trade to team {self.to_team}.")
        return {"message": f"Team {self.from_team} is proposing a trade to team {self.to_team}."}

   @listen(create_trade_proposal)
   def receive_trade_proposal(self, output):
       # Action: check if trade proposal is valid, then trade.
       logging.info(f"Team {self.to_team} is analyzing the trade proposal from team {self.from_team}.")
       return {"message": f"Team {self.to_team} is analyzing the trade proposal from team {self.from_team}."}
