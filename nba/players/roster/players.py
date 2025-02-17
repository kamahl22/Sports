import os

nba_teams = [
    "cleveland-cavaliers", "los-angeles-lakers", "miami-heat", "chicago-bulls", 
    "new-york-knicks", "golden-state-warriors", "brooklyn-nets", "boston-celtics",
    "atlanta-hawks", "charlotte-hornets", "chicago-bulls", "dallas-mavericks", 
    "denver-nuggets", "detroit-pistons", "indiana-pacers", "los-angeles-clippers", 
    "memphis-grizzlies", "minnesota-timberwolves", "new-orleans-pelicans", "orlando-magic", 
    "philadelphia-76ers", "phoenix-suns", "portland-trail-blazers", "sacramento-kings", 
    "san-antonio-spurs", "toronto-raptors", "utah-jazz", "washington-wizards", 
    "houston-rockets", "oklahoma-city-thunder"
]

output_dir = "nba_team_roster"
os.makedirs(output_dir, exist_ok=True)

def generate_team_script(team_slug):
    script_content = f"""import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
from webdriver_manager.chrome import ChromeDriverManager

options = Options()
options.headless = False

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

driver.get("https://www.teamrankings.com/nba/team/{team_slug}/roster")

time.sleep(5)

data = []

try:
    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.XPATH, '//table[contains(@class, "tr-table")]'))
    )
    
    table = driver.find_element(By.XPATH, '//table[contains(@class, "tr-table")]')
    rows = table.find_elements(By.TAG_NAME, "tr")

    for row in rows:
        columns = row.find_elements(By.TAG_NAME, "td")
        if len(columns) >= 10:
            player_data = [col.text.strip() for col in columns[:9]]
            data.append(player_data)

    df = pd.DataFrame(data, columns=["Player Name", "Position", "Games Played", "Minutes Played", 
                                     "Points", "Rebounds", "Assists", "Steals", "Blocks"])
    df.to_csv(f"{team_slug}_roster.csv", index=False)

    print(f"CSV file saved: {team_slug}_roster.csv")

finally:
    driver.quit()
"""

    script_filename = os.path.join(output_dir, f"{team_slug}_roster_scraper.py")
    with open(script_filename, "w") as f:
        f.write(script_content.strip())

    print(f"Script generated: {script_filename}")

for team in nba_teams:
    generate_team_script(team)