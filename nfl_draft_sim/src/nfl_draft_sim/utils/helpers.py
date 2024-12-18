import os
import logging
import pandas as pd

def ensure_dir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)
        logging.info(f"Created directory: {directory}")

def save_data(data: pd.DataFrame, filename: str):
     data.to_csv(filename, index=False)

def set_api_key(api_key_name, env_variable):
    api_key = os.getenv(env_variable)
    if not api_key:
        raise ValueError(f"Environment variable {env_variable} must be set.")
    os.environ[api_key_name] = api_key
