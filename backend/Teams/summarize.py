import os
import pandas as pd
from datetime import datetime

# Choose directories to analyze
team = 'arizona-cardinals'
data_dir = 'data'

# Function to analyze csv file
def analyze_csv(file_path, output_file):
    df = pd.read_csv(file_path)
    file_stats = os.stat(file_path)
    file_created = datetime.fromtimestamp(file_stats.st_ctime)
    file_modified = datetime.fromtimestamp(file_stats.st_mtime)
    
    output_file.write(f"File: {os.path.basename(file_path)}\n")
    output_file.write(f"Last modified: {file_modified}\n")
    output_file.write(f"Created: {file_created}\n") 
    output_file.write(f"File size: {file_stats.st_size/1024:.2f} KB\n\n")
    
    output_file.write(f"Dataset Shape: {df.shape[0]} rows, {df.shape[1]} columns\n")
    output_file.write("Column Data Types:\n")
    output_file.write(str(df.dtypes) + "\n\n")
    output_file.write("Missing Values Count:\n")
    output_file.write(str(df.isnull().sum()) + "\n\n")
    output_file.write("Basic Statistical Summary:\n")
    output_file.write(df.describe().to_string() + "\n\n")
    output_file.write("Columns:\n")
    output_file.write(str(df.columns.tolist()) + "\n\n")
    output_file.write("First few rows:\n")
    output_file.write(df.head().to_string() + "\n")
    output_file.write("\n" + "="*50 + "\n\n")

# Function to analyze Python files
def analyze_python_file(file_path, output_file):
    file_stats = os.stat(file_path)
    file_created = datetime.fromtimestamp(file_stats.st_ctime)
    file_modified = datetime.fromtimestamp(file_stats.st_mtime)
    
    output_file.write(f"Python File: {os.path.basename(file_path)}\n")
    output_file.write(f"Last modified: {file_modified}\n")
    output_file.write(f"Created: {file_created}\n")
    output_file.write(f"File size: {file_stats.st_size/1024:.2f} KB\n\n")
    output_file.write("File Contents:\n")
    output_file.write("```python\n")
    with open(file_path, 'r', encoding='utf-8') as py_file:
        output_file.write(py_file.read())
    output_file.write("\n```\n")
    output_file.write("\n" + "="*50 + "\n\n")

# Function to generate directory tree 
def generate_tree(startpath):
    tree_str = ''
    for root, dirs, files in os.walk(startpath):
        level = root.replace(startpath, '').count(os.sep)
        indent = '|   ' * (level)
        tree_str += f"{indent}{'|-- ' if level > 0 else ''}{os.path.basename(root)}/\n"
        subindent = '|   ' * (level + 1)
        for f in files:
            tree_str += f"{subindent}|-- {f}\n"
    return tree_str

# Get lists of files
team_files = [f for f in os.listdir(team) if f.endswith('.csv')]
data_files = [f for f in os.listdir(data_dir) if f.endswith('.csv')]
# Modified to only get .py files from scripts directory
script_files = [f for f in os.listdir('scripts') if f.endswith('.py')]

# Open output file with UTF-8 encoding
with open('analysis_output.txt', 'w', encoding='utf-8') as output_file:
    # Write file structure tree
    output_file.write("Project File Structure:\n")
    output_file.write(generate_tree('.') + "\n")
    
    # Write directory contents  
    output_file.write("Directory of files:\n")
    output_file.write(str(os.listdir()) + "\n\n")

    # Analyze Python files from scripts directory only
    output_file.write("SCRIPT FILES:\n")
    output_file.write("="*50 + "\n\n")
    for file in script_files:
        analyze_python_file(os.path.join('scripts', file), output_file)

    # Analyze team CSV files
    output_file.write("TEAM CSV FILES:\n") 
    output_file.write("="*50 + "\n\n")
    for file in team_files:
        analyze_csv(os.path.join(team, file), output_file)
        
    # Analyze data directory CSV files
    output_file.write("DATA DIRECTORY CSV FILES:\n")
    output_file.write("="*50 + "\n\n") 
    for file in data_files:
        analyze_csv(os.path.join(data_dir, file), output_file)