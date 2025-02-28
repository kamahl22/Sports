import time
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
from webdriver_manager.chrome import ChromeDriverManager

def format_player_name(player_name):
    """ Converts player name to URL-friendly format """
    formatted_name = player_name.lower().replace(" ", "-")
    formatted_name = re.sub(r"[^a-zA-Z0-9-]", "", formatted_name)  # Remove special characters
    return formatted_name

def get_player_stats(player_name):
    """ Scrapes player stats from TeamRankings.com """
    
    formatted_name = format_player_name(player_name)
    url = f"https://www.teamrankings.com/nba/player/{formatted_name}/stats"

    # Set up Selenium WebDriver
    options = Options()
    options.headless = False
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    driver.get(url)
    time.sleep(5)  # Allow page to load

    data = []

    try:
        # Wait for stats table to be visible
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, '//table[contains(@class, "tr-table")]'))
        )

        # Locate stats table
        table = driver.find_element(By.XPATH, '//table[contains(@class, "tr-table")]')
        rows = table.find_elements(By.TAG_NAME, "tr")

        for row in rows:
            columns = row.find_elements(By.TAG_NAME, "td")
            if len(columns) >= 2:
                stat_category = columns[0].text.strip()
                stat_value = columns[1].text.strip()
                data.append([stat_category, stat_value])

        # Save data to CSV
        df = pd.DataFrame(data, columns=["Stat Category", "Value"])
        df.to_csv(f"{formatted_name}_stats.csv", index=False)

        print(f"CSV file saved: {formatted_name}_stats.csv")

    finally:
        driver.quit()

# Example: Pull stats for Jayson Tatum
player_name = input("Enter the player's full name: ")
get_player_stats(player_name)