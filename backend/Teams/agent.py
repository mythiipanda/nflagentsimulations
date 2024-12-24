# agent.py
import os
import inspect
from cerebras.cloud.sdk import Cerebras
import logging
import re
import sqlite3
from typing import List, Callable, Optional
import json

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

    def _react_loop(self, prompt: str, db_path: str, team_db_path: Optional[str] = None, max_iterations: int = 5) -> str:
        """
        Runs the ReAct loop with a given prompt.

        Args:
            prompt: The initial prompt for the agent.
            db_path: Path to the main database.
            team_db_path: Optional path to the team database.
            max_iterations: Maximum number of iterations before stopping.

        Returns:
            The final response from the agent.
        """
        self.memory.append(f"Initial Prompt: {prompt}")
        current_context = prompt
        previous_actions = set()
        self.db_path = db_path
        self.team_db_path = team_db_path
        
        for i in range(max_iterations):
            logging.info(f"Iteration: {i+1}")
            
            thought = self.generate_thought(current_context)
            self.memory.append(f"Thought {i+1}: {thought}")
            logging.info(f"Thought: {thought}")

            action = self.choose_action(current_context, thought)
            if action in previous_actions:
                return "Respond: I seem to be stuck in a loop."
            previous_actions.add(action)
            
            self.memory.append(f"Action {i+1}: {action}")
            logging.info(f"Action: {action}")
            
            if action.startswith("Respond:"):
                return action[len("Respond:"):].strip()
                
            observation = self.execute_action(action)
            self.memory.append(f"Observation {i+1}: {observation}")
            logging.info(f"Observation: {observation}")
            
            if "Error" not in observation:
                current_context = f"{prompt}\n\nLatest observation: {observation}"
            else:
                return f"Respond: {observation}"

    def generate_thought(self, prompt: str) -> str:
        """
        Generates a thought using the Cerebras API.

        Args:
            prompt: The current prompt for the agent.

        Returns:
            The generated thought as a string, or an error message.
        """
        full_prompt = self.construct_full_prompt(prompt)
        logging.info(f"Sending prompt to LLM:\n{full_prompt}")
        
        try:
            response = self.cerebras_client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "You are a helpful assistant. Follow the ReAct format."},
                    {"role": "user", "content": full_prompt}
                ],
                model="llama3.1-8b",
            )
            thought = response.choices[0].message.content
            logging.info(f"Raw LLM response:\n{thought}")
            return thought
        except Exception as e:
            logging.error(f"Error generating thought: {e}")
            return "Error generating thought."

    def construct_full_prompt(self, prompt: str) -> str:
        """
        Constructs the full prompt with all necessary information.

        Args:
            prompt: The current prompt from the user.

        Returns:
            The complete prompt string with memory, tools, and instructions.
        """
        full_prompt = f"You are {self.name}, your role is {self.role}."
        if self.team:
            full_prompt += f" You are part of the {self.team} team."
        
        full_prompt += "\n\nFollow the ReAct format to solve tasks step by step:"
        full_prompt += "\nThought: Think about what to do based on the prompt and previous observations"
        full_prompt += "\nAction: Choose a specific tool to use or respond with an answer"
        full_prompt += "\nObservation: Describe the result of your action.\n\n"
        
        if self.memory:
            full_prompt += "Previous steps:\n" + "\n".join(self.memory[-3:]) + "\n\n"
        
        full_prompt += "Available Tools:\n"
        for tool in self.tools:
            sig = inspect.signature(tool)
            doc = inspect.getdoc(tool)
            
            # Remove db_path and team_db_path from tool description
            
            params = []
            for param in sig.parameters.values():
                if param.name not in ['db_path', 'team_db_path']:
                    params.append(param)
            
            # Reconstruct signature without the removed parameters
            sig_without_db_paths = sig.replace(parameters=params)
            
            full_prompt += f"- {tool.__name__}{sig_without_db_paths}: {doc}\n"
        
        full_prompt += f"\nCurrent context:\n{prompt}\n\nThought:"
        
        return full_prompt

    def choose_action(self, prompt: str, thought: str) -> str:
        """
        Chooses the next action based on the current thought and available tools.
        
        Args:
            prompt: The current prompt for the agent.
            thought: The agent's current thought.
            
        Returns:
            The chosen action as a string.
        """
        logging.debug(f"Choosing action from thought:\n{thought}")

        # Construct a prompt for the LLM to select the appropriate tool
        tool_descriptions = ""
        for tool in self.tools:
            sig = inspect.signature(tool)
            doc = inspect.getdoc(tool)

            # Remove db_path and team_db_path from tool description for LLM
            params = []
            for param in sig.parameters.values():
                if param.name not in ['db_path', 'team_db_path']:
                    params.append(param)
            sig_without_db_paths = sig.replace(parameters=params)
            tool_descriptions += f"- {tool.__name__}{sig_without_db_paths}: {doc}\n"

        llm_prompt = f"""
Given the following thought and available tools, determine the most appropriate tool to use and its arguments.

Thought: {thought}

Available Tools:
{tool_descriptions}

Respond with a JSON object in the following format:
{{
  "tool": "tool_name",
  "arguments": {{
    "arg_name1": "arg_value1",
    "arg_name2": "arg_value2",
    ...
  }}
}}

If no tool is appropriate, respond with:
{{
  "response": "..."
}}
"""
        logging.info(f"Sending tool selection prompt to LLM: {llm_prompt}")

        try:
            response = self.cerebras_client.chat.completions.create(
                messages=[
                    {"role": "system", "content": "You are a helpful assistant. Choose the best tool and arguments based on the given thought and tool descriptions, and respond with a JSON object."},
                    {"role": "user", "content": llm_prompt}
                ],
                model="llama3.1-8b",
            )
            llm_response = response.choices[0].message.content
            logging.info(f"LLM tool selection response: {llm_response}")

            # Parse the JSON response
            try:
                response_json = json.loads(llm_response)

                if "tool" in response_json:
                    tool_name = response_json["tool"]
                    arguments = response_json.get("arguments", {})
                    # Construct the action string
                    arg_strings = [f"{arg_name}='{arg_value}'" for arg_name, arg_value in arguments.items()]
                    action = f"Action: {tool_name}({', '.join(arg_strings)})"
                    return action
                elif "response" in response_json:
                    return f"Respond: {response_json['response']}"
                else:
                    return f"Respond: I'm not sure what action to take based on: {thought}"

            except json.JSONDecodeError as e:
                logging.error(f"Error decoding JSON response: {e}")
                return f"Respond: Error decoding LLM response: {e}"

        except Exception as e:
            logging.error(f"Error getting tool selection from LLM: {e}")
            return f"Respond: Error getting tool selection: {e}"

    def execute_action(self, action: str) -> str:
        """
        Executes a given action using the appropriate tool.

        Args:
            action: The action string to execute.

        Returns:
            The result of the action execution as a string.
        """
        logging.info(f"Executing action: {action}")
        
        if action.startswith("Action: "):
            action = action[8:]

        try:
            tool_name = action.split('(')[0].strip()
            args_str = action[len(tool_name):].strip('()').strip()

            # Extract arguments from the action string
            
            args = []
            kwargs = {}
            if args_str:
              # Use regex to find arg pairs
              matches = re.findall(r"(\w+)='([^']*)'", args_str)
              for key, value in matches:
                kwargs[key] = value

            tool_func = None
            for tool in self.tools:
                if tool.__name__ == tool_name:
                    tool_func = tool
                    break

            if not tool_func:
                return f"Unknown tool: {tool_name}"
            
            # Pass db_path and team_db_path from agent's context
            
            if 'db_path' in inspect.signature(tool_func).parameters:
                kwargs['db_path'] = self.db_path
            if 'team_db_path' in inspect.signature(tool_func).parameters:
                kwargs['team_db_path'] = self.team_db_path

            logging.info(f"DB path: {self.db_path}")
            logging.info(f"Team DB path: {self.team_db_path}")
            
            result = tool_func(**kwargs)
            return f"Observation: {result}"

        except Exception as e:
            logging.error(f"Error executing action: {e}")
            return f"Error executing action: {e}"

    def convert_arg(self, arg_str: str):
        """
        Converts argument strings to appropriate types.
        """
        if arg_str.startswith("'") and arg_str.endswith("'"):
            return arg_str[1:-1]
        elif arg_str.isdigit():
            return int(arg_str)
        elif arg_str.lower() == 'true':
            return True
        elif arg_str.lower() == 'false':
            return False
        else:
            return arg_str

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