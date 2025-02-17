import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
from webdriver_manager.chrome import ChromeDriverManager

# List of NCAA teams
ncaam_teams = [
    "bradley-braves", "rider-broncos", "radford-highlanders", "missouri-tigers", 
    "st-johns-red-storm"
]

# Define the target folder (lowercase)
output_folder = "ncaam_win_stats"

# Ensure the folder exists
os.makedirs(output_folder, exist_ok=True)

# Function to generate the script for each team
def generate_team_script(team_slug):
    # Create the Python script template
    script_content = f"""
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
from webdriver_manager.chrome import ChromeDriverManager

# Set up the ChromeDriver with webdriver-manager
options = Options()
options.headless = False  # Set to True if you want to run it in headless mode

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# Open the page
driver.get("https://www.teamrankings.com/ncaa-basketball/team/{team_slug}/win-trends")

# Give some extra time for the page to load
time.sleep(5)  # Wait for 5 seconds

# Increase the timeout for waiting
data = []  # List to store the rows

try:
    # Wait for the table to be visible
    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.XPATH, '//table[contains(@class, "tr-table")]'))
    )
    
    # Find the table
    table = driver.find_element(By.XPATH, '//table[contains(@class, "tr-table")]')
    
    # Find the rows of the table
    rows = table.find_elements(By.TAG_NAME, "tr")

    # Loop through the rows and extract the data
    for row in rows:
        columns = row.find_elements(By.TAG_NAME, "td")
        
        # Only process rows with the expected number of columns
        if len(columns) >= 5:
            trend = columns[0].text.strip()
            win_record = columns[1].text.strip()
            win_percent = columns[2].text.strip()
            avg_win_margin = columns[3].text.strip()
            win_plus_minus = columns[4].text.strip()

            # Add the row data to the list
            data.append([trend, win_record, win_percent, avg_win_margin, win_plus_minus])

    # Create a DataFrame from the data
    df = pd.DataFrame(data, columns=["Trend", "Win Record", "Win %", "Avg Win Margin", "Win +/-"])

    # Print the DataFrame (table-like format)
    print(df)

finally:
    driver.quit()  # Close the browser after scraping
"""
    # Define full file path inside the folder
    script_filename = os.path.join(output_folder, f"{team_slug}_win_trends.py")

    # Write the script content to a Python file
    with open(script_filename, "w") as f:
        f.write(script_content.strip())

    print(f"Script for {team_slug} generated successfully in {output_folder}/")

# Generate a script for each team in the list
for team in ncaam_teams:
    generate_team_script(team)