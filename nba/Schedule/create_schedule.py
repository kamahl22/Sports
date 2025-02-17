import os

# List of NBA teams formatted for URL usage
nba_teams = [
    "atlanta-hawks", "boston-celtics", "brooklyn-nets", "charlotte-hornets",
    "chicago-bulls", "cleveland-cavaliers", "dallas-mavericks", "denver-nuggets",
    "detroit-pistons", "golden-state-warriors", "houston-rockets", "indiana-pacers",
    "los-angelrs-clippers", "los-angeles-lakers", "memphis-grizzlies", "miami-heat", "milwaukee-bucks",
    "minnesota-timberwolves", "new-orleans-pelicans", "new-york-knicks", "oklahoma-city-thunder",
    "orlando-magic", "philadelphia-76ers", "phoenix-suns", "portland-trail-blazers",
    "sacramento-kings", "san-antonio-spurs", "toronto-raptors", "utah-jazz", "washington-wizards"
]

# Template for individual team scripts
script_template = """import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
from webdriver_manager.chrome import ChromeDriverManager

# Set up ChromeDriver
options = Options()
options.headless = False  # Set to True for headless mode

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# Open the page
url = "https://www.teamrankings.com/nba/team/{team}"
driver.get(url)

# Wait for page to load
time.sleep(5)

# Scroll to the Results & Schedule section
driver.execute_script("window.scrollBy(0, 600);")  # Scroll down a bit
time.sleep(2)

# Wait for the table
try:
    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.XPATH, '//table[contains(@class, "tr-table")]'))
    )

    # Locate all tables
    tables = driver.find_elements(By.XPATH, '//table[contains(@class, "tr-table")]')

    if tables:
        print(f"Found {{len(tables)}} tables for {team_name}. Selecting the most likely one...")

        schedule_table = None
        for table in tables:
            if "Date" in table.text:  # Ensure correct table
                schedule_table = table
                break

        if schedule_table:
            rows = schedule_table.find_elements(By.TAG_NAME, "tr")

            data = []
            for row in rows:
                columns = row.find_elements(By.TAG_NAME, "td")
                if len(columns) >= 6:  # Ensure correct column count
                    date = columns[0].text.strip()
                    opponent = columns[1].text.strip()
                    result = columns[2].text.strip()
                    location = columns[3].text.strip()
                    win_loss = columns[4].text.strip()
                    division = columns[5].text.strip()

                    data.append([date, opponent, result, location, win_loss, division])

            if data:
                df = pd.DataFrame(data, columns=["Date", "Opponent", "Result", "Location", "W/L", "Division"])
                df.to_csv("{team}_schedule_results.csv", index=False)
                print(f"Saved {team}_schedule_results.csv")
            else:
                print(f"Table found for {team_name}, but no data extracted. Possible dynamic loading issue.")
        else:
            print(f"No matching schedule table found for {team_name}.")
    else:
        print(f"No tables found for {team_name}.")

except Exception as e:
    print(f"Error scraping {team_name}: {{e}}")

# Close the browser after scraping
driver.quit()
"""

# Directory to save the scripts
output_dir = "nba_team_schedule"
os.makedirs(output_dir, exist_ok=True)

# Generate a separate script for each team
for team in nba_teams:
    team_script = script_template.format(team=team, team_name=team.replace("-", " ").title())
    script_filename = os.path.join(output_dir, f"{team}_schedule.py")

    with open(script_filename, "w", encoding="utf-8") as f:
        f.write(team_script)

    print(f"Created script: {script_filename}")

print("All team scripts have been generated successfully!")