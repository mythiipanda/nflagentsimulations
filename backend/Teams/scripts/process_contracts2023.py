import csv
import os
from collections import defaultdict

def filter_active_contracts_with_restructures(input_filename, output_filename, target_year=2023):
    """
    Filters contracts and removes specified columns from active 2023 contracts.
    Uses gsis_id if available, falls back to player name.
    Keeps only most recent contract per player.
    """
    active_contracts_2023 = defaultdict(list)
    header = None
    
    columns_to_remove = [
        "position", "is_active", "team", "player_page", "otc_id",
        "date_of_birth", "height", "weight", "college", "draft_year", 
        "draft_round", "draft_overall", "draft_team"
    ]

    with open(input_filename, 'r', newline='', encoding='utf-8') as infile:
        reader = csv.reader(infile)
        header = next(reader)
        
        indices_to_remove = [header.index(col) for col in columns_to_remove if col in header]
        keep_indices = [i for i in range(len(header)) if i not in indices_to_remove]
        new_header = [header[i] for i in keep_indices]

        gsis_id_index = header.index('gsis_id')
        player_index = header.index('player')
        year_signed_index = 4

        for row in reader:
            try:
                player_name = row[player_index]
                gsis_id = row[gsis_id_index] if row[gsis_id_index] != 'NA' else None
                year_signed = int(row[year_signed_index])
                years = int(row[5])

                if year_signed <= target_year and (year_signed + years) >= (target_year - 1):
                    filtered_row = [row[i] for i in keep_indices]
                    # Store with both keys if gsis_id exists
                    if gsis_id:
                        active_contracts_2023[gsis_id].append((year_signed, filtered_row))
                    active_contracts_2023[player_name].append((year_signed, filtered_row))

            except ValueError:
                print(f"Skipping row due to invalid year_signed or years: {row}")
            except IndexError:
                print(f"Skipping row due to missing columns: {row}")

    # Get most recent contract for each key
    latest_contracts = []
    processed_rows = set()  # Track unique rows
    
    for contracts in active_contracts_2023.values():
        if contracts:
            # Sort by year_signed and get most recent
            latest = max(contracts, key=lambda x: x[0])[1]
            # Convert to tuple for set comparison
            row_tuple = tuple(latest)
            if row_tuple not in processed_rows:
                latest_contracts.append(latest)
                processed_rows.add(row_tuple)

    os.makedirs(os.path.dirname(output_filename), exist_ok=True)

    with open(output_filename, 'w', newline='', encoding='utf-8') as outfile:
        writer = csv.writer(outfile)
        writer.writerow(new_header)
        writer.writerows(latest_contracts)

    print(f"Processed {len(latest_contracts)} unique contracts")

if __name__ == "__main__":
    input_file = 'data/historical_contracts_no_cols.csv'
    output_file = 'data/active_contracts_2023.csv'
    filter_active_contracts_with_restructures(input_file, output_file)
    print(f"Filtered contracts active in 2023 with removed columns saved to {output_file}")