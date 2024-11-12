import pandas as pd
from sklearn.preprocessing import MinMaxScaler

def preprocess_csv(input_file, output_file, columns_to_remove, columns_to_normalize):
    # Read the CSV file
    df = pd.read_csv(input_file)
    
    # Remove specified columns
    df.drop(columns=columns_to_remove, inplace=True)
    
    # Normalize specified columns
    scaler = MinMaxScaler()
    df[columns_to_normalize] = scaler.fit_transform(df[columns_to_normalize])
    
    # Save the processed DataFrame to another CSV file
    df.to_csv(output_file, index=False)

# Example usage
input_file = 'input.csv'
output_file = 'output.csv'
columns_to_remove = ['column1', 'column2']
columns_to_normalize = ['column3', 'column4']

preprocess_csv(input_file, output_file, columns_to_remove, columns_to_normalize)