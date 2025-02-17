import time
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

driver.get("https://www.teamrankings.com/nba/team/detroit-pistons/roster")

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
    df.to_csv(f"detroit-pistons_roster.csv", index=False)

    print(f"CSV file saved: detroit-pistons_roster.csv")

finally:
    driver.quit()