library(nflreadr)
library(dplyr)

load_historical_injuries <- function(start_year, end_year) {
  # Create data directory
  if (!dir.exists("data")) {
    dir.create("data")
  }
  
  # Process each year
  for (year in start_year:end_year) {
    print(paste("Loading injury data for:", year))
    
    tryCatch({
      # Load injury reports
      injury_reports <- load_injuries(seasons = year)
      
      if (!is.null(injury_reports)) {
        # Save to CSV
        output_file <- paste0("data/injury_reports_", year, ".csv")
        write.csv(injury_reports, output_file, row.names = FALSE)
        print(paste("Saved injury reports to", output_file))
        
        # Print summary
        print(paste("Total injuries:", nrow(injury_reports)))
        print(paste("Unique players:", length(unique(injury_reports$player))))
      } else {
        print(paste("No injury data found for year", year))
      }
    }, error = function(e) {
      message(paste("Error processing year", year, ":"))
      message(e)
    })
  }
}

# Load data for 2009-2024
load_historical_injuries(2009, 2024)