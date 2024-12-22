library(nflreadr)
library(dplyr)
library(tidyr)

load_and_save_nflverse_data <- function(year) {
  # Create the data/ directory if it doesn't exist
  if (!dir.exists("data")) {
    dir.create("data")
  }

  # Load schedule data
  tryCatch({
    schedule_data <- load_schedules(year)
    write.csv(schedule_data, paste0("data/schedule_data_", year, ".csv"), row.names = FALSE)
    print(paste("Saved schedule data to data/schedule_data_", year, ".csv"))
  }, error = function(e) {
    message("Error loading or saving schedule data:")
    message(e)
  })

  # Load roster data
  tryCatch({
    roster_data <- load_rosters(year)
    write.csv(roster_data, paste0("data/roster_data_", year, ".csv"), row.names = FALSE)
    print(paste("Saved roster data to data/roster_data_", year, ".csv"))
  }, error = function(e) {
    message("Error loading or saving roster data:")
    message(e)
  })

  # Load team data
  tryCatch({
    team_data <- load_teams()
    write.csv(team_data, "data/team_data.csv", row.names = FALSE)
    print("Saved team data to data/team_data.csv")
  }, error = function(e) {
    message("Error loading or saving team data:")
    message(e)
  })

  # Load injury reports and save to team-specific folders
  tryCatch({
    injury_reports <- load_injuries(seasons = year)

    if (!is.null(injury_reports)) {
      # Team name mapping (full name to abbreviation)
      team_mapping <- c(
        "arizona-cardinals" = "ARI",
        "atlanta-falcons" = "ATL",
        "baltimore-ravens" = "BAL",
        "buffalo-bills" = "BUF",
        "carolina-panthers" = "CAR",
        "chicago-bears" = "CHI",
        "cincinnati-bengals" = "CIN",
        "cleveland-browns" = "CLE",
        "dallas-cowboys" = "DAL",
        "denver-broncos" = "DEN",
        "detroit-lions" = "DET",
        "green-bay-packers" = "GB",
        "houston-texans" = "HOU",
        "indianapolis-colts" = "IND",
        "jacksonville-jaguars" = "JAX",
        "kansas-city-chiefs" = "KC",
        "las-vegas-raiders" = "LV",
        "los-angeles-rams" = "LA",
        "los-angeles-chargers" = "LAC",
        "miami-dolphins" = "MIA",
        "minnesota-vikings" = "MIN",
        "new-england-patriots" = "NE",
        "new-orleans-saints" = "NO",
        "new-york-giants" = "NYG",
        "new-york-jets" = "NYJ",
        "philadelphia-eagles" = "PHI",
        "pittsburgh-steelers" = "PIT",
        "san-francisco-49ers" = "SF",
        "seattle-seahawks" = "SEA",
        "tampa-bay-buccaneers" = "TB",
        "tennessee-titans" = "TEN",
        "washington-commanders" = "WAS"
      )

      for (team in names(team_mapping)) {
        team_folder <- file.path(team)
        dir.create(team_folder, showWarnings = FALSE)
        
        # Filter injury reports based on team abbreviation
        team_abbr <- team_mapping[team]
        team_injuries <- injury_reports %>% filter(team == team_abbr)

        if (nrow(team_injuries) > 0) {
          write.csv(team_injuries, file.path(team_folder, paste0(team, "_injuries_", year, ".csv")), row.names = FALSE)
          print(paste("Saved", team, "injury reports to", team_folder))
        } else {
          print(paste("No injury data found for", team, "in", year))
        }
      }
    }
  }, error = function(e) {
    message("Error loading or saving injury reports:")
    message(e)
  })
}

# Example Usage
load_and_save_nflverse_data(2024)