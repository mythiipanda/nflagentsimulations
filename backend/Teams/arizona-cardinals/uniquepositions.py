import csv

def find_unique_positions():
    csv_files = [
        r'c:/Users/15980/Downloads/FootballProjects/backend/Teams/arizona-cardinals/defense_2023.csv',
        r'c:/Users/15980/Downloads/FootballProjects/backend/Teams/arizona-cardinals/offense_2023.csv',
        r'c:/Users/15980/Downloads/FootballProjects/backend/Teams/arizona-cardinals/special_teams_2023.csv'
    ]
    unique_positions = set()
    unique_depth_chart_positions = set()
    roster_unique_positions = set()
    roster_unique_depth_chart_positions = set()

    for csv_file in csv_files:
        with open(csv_file, 'r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                position = row.get('Position') or row.get('position')
                if position:
                    unique_positions.add(position)

    # Process roster.csv separately
    roster_file = r'c:/Users/15980/Downloads/FootballProjects/backend/Teams/arizona-cardinals/roster.csv'
    with open(roster_file, 'r', newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            position = row.get('position')
            depth_chart_position = row.get('depth_chart_position')
            if position:
                roster_unique_positions.add(position)
            if depth_chart_position:
                roster_unique_depth_chart_positions.add(depth_chart_position)

    print("Unique positions from PFF CSVs:", unique_positions)
    print("Unique positions from roster.csv:", roster_unique_positions)
    print("Unique depth chart positions from roster.csv:", roster_unique_depth_chart_positions)

if __name__ == "__main__":
    find_unique_positions()