import requests
from bs4 import BeautifulSoup
import csv

url = "https://www.ea.com/games/madden-nfl/ratings"
response = requests.get(url)
soup = BeautifulSoup(response.text, "html.parser")

rows = soup.find_all("tr", class_="Table_row__4INyY")

players = []
for row in rows:
    player = {}

    name_cell = row.find("td", {"data-type": "profile"})
    if name_cell:
        profile_content = name_cell.find("div", class_="Table_profileContent__Lna_E")
        if profile_content:
            player["name"] = profile_content.text.strip()

    position_cell = row.find("td", {"data-type": "profile"})
    if position_cell:
        position_tag = position_cell.find("span", class_="Table_tag__FeM31")
        if position_tag:
            player["position"] = position_tag.text.strip()

    team_cell = row.find("td", {"data-type": "team"})
    if not team_cell:
        team_cell = row.find("td", style=lambda value: value and "order-sm:3" in value and "order-md:4" in value)
    if team_cell:
        team_image_wrap = team_cell.find("div", class_="Picture_responsiveImageWrap__mI2vU")
        if team_image_wrap:
            team_image = team_image_wrap.find("img")
            if team_image:
                player["team"] = team_image["alt"]

    # Extract all stats (OVR, SPD, STR, etc.)
    stat_cells = row.find_all("td", {"data-type": "group"})  # or {"data-type": "stat"} if present. Adjust accordingly.
    if not stat_cells:  # If data-type not found, find by broader criteria
        stat_cells_parent = row.find("td", class_="Table_rowBlock__Ym9Qr")
        if stat_cells_parent:
             stat_cells = stat_cells_parent.find_all("td", {"data-type": "group"})


    for cell in stat_cells:
        stat_div = cell.find("div", class_="Table_statCell__lGdI4")
        if stat_div:
            stat_label = stat_div.get("data-label", "").strip()
            stat_value_span = stat_div.find("span", class_="Table_statCellValue__0G9QI")
            if stat_value_span:
                player[stat_label] = stat_value_span.text.strip()[0:2]


    ovr_cell = row.find("td", style=lambda value: value and "order-sm:5" in value ) # Find by style
    if ovr_cell: # extract OVR (overall) separately if its structure is different
      stat_div = ovr_cell.find("div", class_="Table_statCell__lGdI4")
      if stat_div:
        stat_label = stat_div.get("data-label", "").strip()
        stat_value_span = stat_div.find("span", class_="Table_statCellValue__0G9QI")
        if stat_value_span:
            player[stat_label] = stat_value_span.text.strip()[:2]

    if player:
        players.append(player)

for player in players:
    print(player)

# Save to CSV
keys = players[0].keys() if players else []
with open('players.csv', 'w', newline='') as output_file:
    dict_writer = csv.DictWriter(output_file, fieldnames=keys)
    dict_writer.writeheader()
    dict_writer.writerows(players)