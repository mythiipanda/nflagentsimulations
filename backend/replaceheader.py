import csv

# Define the header
header = ["rank", "college", "face", "name", "33rd", "ATH", "BR", "Buzz", "CBS", "DT", "ESPN", "NBC", "NFL", "PFF", "PFN", "Ring", "SBN", "Tank", "USA", "WF", "Yahoo", "SD", "Avg"]

# Open a CSV file for writing
with open('nfl_draft_2024.csv', 'w', newline='') as csv_file:
    csv_writer = csv.writer(csv_file)
    csv_writer.writerow(header)