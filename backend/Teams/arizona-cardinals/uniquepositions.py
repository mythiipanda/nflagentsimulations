import csv

def find_unique_positions():
    # Define CSV files categorized by their type
    csv_files = {
        'defense': [
            r'c:/Users/15980/Downloads/FootballProjects/backend/Teams/arizona-cardinals/defense_2023.csv'
        ],
        'offense': [
            r'c:/Users/15980/Downloads/FootballProjects/backend/Teams/arizona-cardinals/offense_2023.csv'
        ],
        'special_teams': [
            r'c:/Users/15980/Downloads/FootballProjects/backend/Teams/arizona-cardinals/special_teams_2023.csv'
        ]
    }

    # Initialize dictionaries to hold unique positions per category
    unique_positions = {
        'defense': set(),
        'offense': set(),
        'special_teams': set()
    }
    roster_unique_positions = set()
    roster_unique_depth_chart_positions = set()

    # Process each category's CSV files
    for category, files in csv_files.items():
        for csv_file in files:
            try:
                with open(csv_file, 'r', newline='', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        position = row.get('Position') or row.get('position')
                        if position:
                            unique_positions[category].add(position)
            except Exception as e:
                print(f"Error processing {csv_file}: {e}")

    # Process roster.csv separately
    roster_file = r'c:/Users/15980/Downloads/FootballProjects/backend/Teams/arizona-cardinals/roster.csv'
    try:
        with open(roster_file, 'r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                position = row.get('position')
                depth_chart_position = row.get('depth_chart_position')
                if position:
                    roster_unique_positions.add(position)
                if depth_chart_position:
                    roster_unique_depth_chart_positions.add(depth_chart_position)
    except Exception as e:
        print(f"Error processing {roster_file}: {e}")

    # Print unique positions separately for each category
    print("\nUnique Positions from Defense CSVs:")
    print("-" * 30)
    for pos in sorted(unique_positions['defense']):
        print(pos)

    print("\nUnique Positions from Offense CSVs:")
    print("-" * 30)
    for pos in sorted(unique_positions['offense']):
        print(pos)

    print("\nUnique Positions from Special Teams CSVs:")
    print("-" * 30)
    for pos in sorted(unique_positions['special_teams']):
        print(pos)

    print("\nUnique Positions from roster.csv:")
    print("-" * 30)
    for pos in sorted(roster_unique_positions):
        print(pos)

    print("\nUnique Depth Chart Positions from roster.csv:")
    print("-" * 30)
    for pos in sorted(roster_unique_depth_chart_positions):
        print(pos)

if __name__ == "__main__":
    find_unique_positions()