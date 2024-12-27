import os
import inspect
from cerebras.cloud.sdk import Cerebras
import logging
import re
import sqlite3
from typing import List, Callable, Optional
import json
from tools import POSITION_MAPPINGS, TEAM_MAPPINGS

class Agent:
    def __init__(self, name: str, role: str, team: Optional[str] = None, tools: Optional[List[Callable]] = None, memory_file: Optional[str] = None, cerebras_client: Optional[Cerebras] = None):
        self.name = name
        self.role = role
        self.team = team
        self.tools = tools or []
        self.cerebras_client = cerebras_client or Cerebras()
        self.memory = []
        self.memory_file = memory_file
        self.load_memory()
        self.db_path = None  # Store db_path at the agent level
        self.team_db_path = None # Store team_db_path at the agent level
        self.state = "Initial"  # Initial state
        self.position_mappings = POSITION_MAPPINGS
        self.team_mappings = TEAM_MAPPINGS
        self.used_tools = set()  # Track used tools per task
        self.task_complete = False # Flag for task completion

    def _react_loop(
        self,
        prompt: str,
        db_path: str,
        team_db_path: Optional[str] = None,
        max_iterations: int = 5
    ) -> str:
        """
        Main loop for agent's thought, action, and observation process.
        """
        self.memory.append(f"Initial Prompt: {prompt}")
        current_context = prompt
        self.db_path = db_path
        self.team_db_path = team_db_path
        self.state = "Initial"
        self.used_tools = set() # Reset used tools
        self.task_complete = False

        for i in range(max_iterations):
            logging.info(f"Iteration: {i+1}, State: {self.state}")

            # Generate thought
            thought = self.generate_thought(current_context)
            if "Error" in thought:
                self.memory.append(f"Error in thought generation: {thought}")
                current_context = f"{prompt}\n\nError in thought generation: {thought}"
                self.state = "Error"
                continue

            self.memory.append(f"Thought {i+1}: {thought}")
            logging.info(f"Thought: {thought}")

            # Check for task completion after generating a thought
            if self.is_task_complete(thought):
                return self.final_response()

            # Choose action based on thought and state
            action_dict = self.choose_action(current_context, thought)

            # Handle errors in action choice
            if isinstance(action_dict, dict) and "error" in action_dict:
                error_message = action_dict["error"]
                self.memory.append(f"Error in action choice: {error_message}")
                current_context = f"{prompt}\n\nThought: {thought}\nError in action choice: {error_message}"
                self.state = "Error"
                continue

            # Handle direct responses / task completion
            if isinstance(action_dict, dict) and "response" in action_dict:
                self.memory.append(f"Final Response: {action_dict['response']}")
                return action_dict["response"]

            # At this point, we expect the action_dict to contain a "tool" key
            action = action_dict.get("tool")
            if not action:
                error_message = "No tool specified in action_dict."
                self.memory.append(f"Error in action choice: {error_message}")
                current_context = f"{prompt}\n\nThought: {thought}\nError in action choice: {error_message}"
                self.state = "Error"
                continue

            self.used_tools.add(action)

            self.memory.append(f"Action {i+1}: {action}({action_dict.get('arguments', {})})")
            logging.info(f"Action: {action}")
            logging.info(f"Action arguments: {action_dict['arguments']}")

            # Execute the action and get the observation
            observation = self.execute_action(action_dict)

            # --- STRICT OBSERVATION HANDLING ---
            if "Error" in observation:
                self.memory.append(f"Error executing action: {observation}")
                current_context = f"{prompt}\n\nThought: {thought}\nAction: {action}({action_dict.get('arguments', {})})\nError executing action: {observation}"
                self.state = "Error"
                continue  # Skip to the next iteration if there's an error
            else:
                self.memory.append(f"Observation {i+1}: {observation}")  # Only add observation if successful
                current_context = f"{prompt}\n\nThought: {thought}\nObservation: {observation}"

            # Update state based on action and observation
            self.update_state(action, observation)

        return "Respond: Maximum iterations reached without resolution"
    
    def is_task_complete(self, thought: str) -> bool:
        """
        Checks if the thought indicates that the task has been completed.
        """
        completion_cues = [
            "task is complete",
            "task has been completed",
            "achieved the goal",
            "completed the task",
            "all steps have been taken",
            "final answer",
            "final response",
            "final observation",
            "that completes the task",
            "the objective has been met"
        ]
        
        # Check if the thought ends with the request to return the final result
        return_final_result_cues = [
            "return the final result",
            "present the final result",
            "give the final response",
            "return the final answer",
            "provide the final answer",
            "give the complete response",
            "present the complete response"
        ]
        
        lower_thought = thought.lower()
        if any(cue in lower_thought for cue in completion_cues):
            self.task_complete = True
            logging.info("Task completion detected in thought.")

        # If thought ends with a cue to return the final result, indicate that the next response should be the final one
        if any(cue in lower_thought.split('.')[-1].strip() for cue in return_final_result_cues):
            self.state = "TaskComplete"
            logging.info("Detected request to return final result. Setting state to TaskComplete.")
            return False

        return self.task_complete
    
    def final_response(self) -> str:
        """
        Generates the final response to the initial prompt.
        """
        logging.info("Generating final response.")
        final_prompt = f"""
        You have completed the task. Now, provide the final response to the initial prompt:
        
        Initial Prompt: {self.memory[0].split('Initial Prompt: ')[1]}
        
        Here are the steps taken:
        
        {self.construct_full_prompt_thought('')}
        
        Provide a concise and direct answer to the initial prompt based on the observations made. Make sure your response directly relates to the initial prompt.
        """

        try:
            response = self.cerebras_client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "You are a helpful assistant. Provide the final response based on the steps taken and observations made."},
                    {"role": "user", "content": final_prompt}
                ],
                model="llama3.1-8b",
            )
            final_response = response.choices[0].message.content
            logging.info(f"Final response generated: {final_response}")
            return final_response
        except Exception as e:
            logging.error(f"Error generating final response: {e}")
            return f"Error generating final response: {e}"

    def update_state(self, action: str, observation: str):
        """
        Updates the agent's state based on the action taken and the observation received.
        """
        if action == "get_team_roster":
            if "Error" not in observation:
                self.state = "RosterAcquired"
            else:
                self.state = "Error"
        elif action == "get_ranked_players":
            if "Error" not in observation:
                self.state = "PlayersRanked"
            else:
                self.state = "Error"
        elif action == "query_team_stats":
            if "Error" not in observation:
                self.state = "TeamStatsAnalyzed"
            else:
                self.state = "Error"
        elif action == "get_position_stats" or action == "get_position_group":
            if "Error" not in observation:
                self.state = "InvestigatingPositionStats"
            else:
                self.state = "Error"
        elif action == "get_player_stats":
            if "Error" not in observation:
                self.state = "InvestigatingPotentialWeakness"
            else:
                self.state = "Error"

        elif "Error" in observation:
            self.state = "Error"
        elif self.state == "Error":
            self.state = "TryingAgain"
        else:
            self.state = "Processing"
        logging.info(f"State updated to: {self.state}")

    def generate_thought(self, prompt: str) -> str:
        """
        Generates a thought using the Cerebras API.

        Args:
            prompt: The current prompt for the agent.

        Returns:
            The generated thought as a string, or an error message.
        """
        full_prompt = self.construct_full_prompt_thought(prompt)
        logging.info(f"Sending prompt to LLM:\n{full_prompt}")

        try:
            response = self.cerebras_client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "You are an agent for NFL analysis, do not use any data except from tools available to you. Follow the ReAct format."},
                    {"role": "user", "content": full_prompt}
                ],
                model="llama3.1-8b",
            )
            thought = response.choices[0].message.content
            logging.info(f"Raw LLM response:\n{thought}")
            return thought
        except Exception as e:
            logging.error(f"Error generating thought: {e}")
            return f"Error generating thought: {e}"

    def construct_full_prompt_thought(self, prompt: str) -> str:
        """
        Constructs the full prompt for thought generation with all necessary information.

        Args:
            prompt: The current prompt from the user.

        Returns:
            The complete prompt string with memory, tools, and instructions.
        """
        full_prompt = f"You are {self.name}, your role is {self.role}."
        if self.team:
            full_prompt += f" You are part of the {self.team} team."

        full_prompt += "\n\nFollow the ReAct format to solve tasks step by step:"
        full_prompt += "\nThought: Think about what to do based on the prompt and previous observations."
        full_prompt += "\nAction: Choose a specific tool to use or respond with an answer."
        full_prompt += "\nObservation: **Only make observations immediately after a tool has successfully executed. Do not generate observations unless you have actually used a tool and it has returned a result. Fabricating observations will lead to incorrect conclusions.**\n\n"

        if self.memory:
            full_prompt += "Previous steps:\n" + "\n".join(self.memory[-5:]) + "\n\n"

        full_prompt += f"\nCurrent context:\n{prompt}\n\nThought:"
        return full_prompt

    def get_tool_descriptions(self) -> str:
        """Dynamically generates descriptions for available tools."""
        tool_descriptions = ""
        for tool in self.tools:
            sig = inspect.signature(tool)
            doc = inspect.getdoc(tool)

            params = []
            for param in sig.parameters.values():
                if param.name not in ['db_path', 'team_db_path']:
                    params.append(param)

            sig_without_db_paths = sig.replace(parameters=params)
            tool_descriptions += f"- `{tool.__name__}{sig_without_db_paths}`: {doc}\n"
        return tool_descriptions

    def construct_full_prompt_action(self, prompt: str, thought: str) -> str:
        full_prompt = f"You are {self.name}, your role is {self.role}."
        if self.team:
            full_prompt += f" You are part of the {self.team} team."

        full_prompt += "\n\nFollow the ReAct format to solve tasks step by step:"
        full_prompt += "\nThought: Think about what to do based on the prompt and previous observations."
        full_prompt += "\nAction: Choose a specific tool to use or respond with an answer. **Always format your action as a JSON object like this:**\n```json\n{{\"tool\": \"tool_name\", \"arguments\": {{\"arg_name\": \"arg_value\"}}}}\n```\n"
        full_prompt += "\nObservation: **Only make observations after executing a tool. Do not generate observations unless you have actually used a tool.**\n\n"

        # Provide examples of tool usage
        full_prompt += "Examples:\n"
        full_prompt += "Thought: I need to know the current roster of the Arizona Cardinals.\n"
        full_prompt += "Action: ```json\n{\"tool\": \"get_team_roster\", \"arguments\": {\"team_name\": \"Arizona Cardinals\"}}\n```\n"
        full_prompt += "Observation: Roster for Arizona Cardinals:\nMatt Prater (#5.0) - K\nColt McCoy (#12.0) - QB\nAaron Brewer (#46.0) - LS\nKelvin Beachum (#68.0) - OL\nDamien Williams (#29.0) - RB\n...\n```\n\n"
        full_prompt += "Thought: I need to get the stats for the quarterback, Kyler Murray.\n"
        full_prompt += "Action: ```json\n{\"tool\": \"get_player_stats\", \"arguments\": {\"player_name\": \"Kyler Murray\"}}\n```\n"
        full_prompt += "Observation: Player: Kyler Murray\nJerseyNumber: 1\nPosition: QB\nGamesPlayed: 15\nOverall Grade: 88.5\nTotalSnaps: 980\n```\n\n"

        if self.memory:
            full_prompt += "Previous steps:\n" + "\n".join(self.memory[-5:]) + "\n\n"

        full_prompt += "Available Tools:\n"
        full_prompt += self.get_tool_descriptions()

        full_prompt += f"\nThought: {thought}"
        full_prompt += "\nAction: ```json\n"
        return full_prompt

    def choose_action(self, prompt: str, thought: str) -> dict:
        logging.info(f"Choosing action based on thought: {thought}, State: {self.state}")

        # Define state-based tool suggestions
        if self.state == "Initial":
            suggested_tools = ["get_team_roster", "get_draft_order", "query_team_stats"]
        elif self.state == "RosterAcquired":
            suggested_tools = ["get_ranked_players", "query_team_stats"]
        elif self.state == "PlayersRanked":
            suggested_tools = ["query_team_stats", "get_position_group"]
        elif self.state == "TeamStatsAnalyzed":
            suggested_tools = ["get_position_stats", "get_position_group", "get_player_stats"]
        elif self.state == "InvestigatingPositionStats":
            suggested_tools = ["get_position_stats", "get_position_group", "get_player_stats"]
        elif self.state == "ComparingPositionGroups":
            suggested_tools = ["get_position_group", "get_player_stats"]
        elif self.state == "InvestigatingPotentialWeakness":
            suggested_tools = ["get_player_stats"]
        elif self.state == "AnalyzingWeaknesses":
            suggested_tools = []
        elif self.state == "Error":
            suggested_tools = ["get_team_roster", "get_ranked_players", "query_team_stats"]
        elif self.state == "TaskComplete":
            return {"response": self.final_response()}
        else:
            suggested_tools = [tool.__name__ for tool in self.tools]

        llm_prompt = f"""{self.construct_full_prompt_action(prompt, thought)}
        Based on the current thought, available tools, and agent state, select the most appropriate tool and its arguments.

        Current state: {self.state}

        Suggested tools for this state (use only if relevant to the thought): {', '.join(suggested_tools)}

        You MUST respond with valid JSON.

        To use a tool, respond with a JSON object in the following format:
        ```json
        {{
        "tool": "tool_name",
        "arguments": {{
            "arg_name1": "arg_value1",
            "arg_name2": "arg_value2",
            ...
        }}
        }}
        ```

        If you have completed the task and can respond to the original prompt, use the "response" key:
        ```json
        {{
        "response": "Your final response here"
        }}
        ```
        """
        logging.info(f"Sending action selection prompt to LLM: {llm_prompt}")

        try:
            response = self.cerebras_client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "You are a helpful assistant. Choose the best tool and arguments based on the given thought, tool descriptions, agent state, and suggested tools, or respond directly if you have the answer. Respond with a JSON object."},
                    {"role": "user", "content": llm_prompt}
                ],
                model="llama3.1-8b",
            )
            llm_response = response.choices[0].message.content
            logging.info(f"LLM action selection response: {llm_response}")

            # Extract JSON from Markdown code block, if present
            if "```json" in llm_response:
                llm_response = llm_response.split("```json")[1].split("```")[0].strip()

            # Parse the JSON response
            try:
                response_json = json.loads(llm_response)

                # Check if the response is directly a string (indicating a direct response)
                if isinstance(response_json, str):
                    return {"response": response_json}

                # Validate the structure of the JSON response
                if "tool" not in response_json and "response" not in response_json:
                    return {"error": f"Invalid response format: missing 'tool' or 'response' key in {response_json}"}
                elif "tool" in response_json:
                    tool_name = response_json["tool"]
                    arguments = response_json.get("arguments", {})

                    # Validate tool against suggested tools if available
                    if suggested_tools and tool_name not in suggested_tools:
                        logging.warning(f"Tool '{tool_name}' chosen, but not suggested for state '{self.state}'.")

                    # Validate that the tool exists
                    if tool_name not in [tool.__name__ for tool in self.tools]:
                        return {"error": f"Invalid tool: '{tool_name}' is not available."}

                    # Validate arguments and map positions if necessary
                    if tool_name in ["get_position_stats", "get_position_group"]:
                        if "position" in arguments:
                            roster_position = arguments["position"]
                            pff_position = self.position_mappings.get(roster_position)
                            if pff_position:
                                arguments["position"] = pff_position
                            else:
                                return {"error": f"Invalid roster position: {roster_position}"}
                    elif tool_name == "get_team_roster":
                        if "team_name" in arguments:
                            arguments["team_name"] = self.team_mappings.get(arguments["team_name"].lower().replace(" ", "-"), arguments["team_name"])
                    elif tool_name == "query_team_stats":
                        # No specific argument mapping needed for this tool yet, but can be added if required
                        pass

                    return {"tool": tool_name, "arguments": arguments}
                elif "response" in response_json:
                    return {"response": response_json["response"]}

            except json.JSONDecodeError as e:
                logging.error(f"Error decoding JSON response: {e}")
                return {"error": f"Error decoding LLM response: {e}"}

        except Exception as e:
            logging.error(f"Error getting tool selection from LLM: {e}")
            return {"error": f"Error getting tool selection: {e}"}

    def execute_action(self, action_dict: dict) -> str:
        """
        Executes a given action using the appropriate tool.

        Args:
            action_dict: A dictionary containing the 'tool' and its 'arguments'.

        Returns:
            The result of the action execution as a string.
        """
        tool_name = action_dict.get("tool")
        arguments = action_dict.get("arguments", {})

        if not tool_name:
            return "Error: No tool specified in the action."

        logging.info(f"Executing action: {tool_name} with arguments: {arguments}")

        try:
            tool_func = None
            for tool in self.tools:
                if tool.__name__ == tool_name:
                    tool_func = tool
                    break

            if not tool_func:
                return f"Error: Unknown tool: {tool_name}"

            # Pass db_path and team_db_path from agent's context
            tool_signature = inspect.signature(tool_func)
            if 'db_path' in tool_signature.parameters:
                arguments['db_path'] = self.db_path
            if 'team_db_path' in tool_signature.parameters:
                arguments['team_db_path'] = self.team_db_path

            # Validate arguments before execution
            for param_name, param in tool_signature.parameters.items():
                if param_name not in arguments and param.default == inspect.Parameter.empty and param_name not in ['db_path', 'team_db_path']:
                    return f"Error: Missing argument '{param_name}' for tool '{tool_name}'"

            logging.info(f"DB path: {self.db_path}")
            logging.info(f"Team DB path: {self.team_db_path}")

            result = tool_func(**arguments)
            return result

        except Exception as e:
            logging.error(f"Error executing action: {tool_name} with arguments: {arguments}. Error: {e}")
            return f"Error executing action: {e}"

    def save_memory(self):
        """Saves the agent's memory to a file."""
        if self.memory_file:
            try:
                with open(self.memory_file, "w") as f:
                    f.write("\n".join(self.memory))
                logging.info(f"Memory saved to {self.memory_file}")
            except Exception as e:
                logging.error(f"Error saving memory to {self.memory_file}: {e}")

    def load_memory(self):
        """Loads the agent's memory from a file."""
        if self.memory_file and os.path.exists(self.memory_file):
            try:
                with open(self.memory_file, "r") as f:
                    self.memory = f.read().splitlines()
                logging.info(f"Memory loaded from {self.memory_file}")
            except Exception as e:
                logging.error(f"Error loading memory from {self.memory_file}: {e}")