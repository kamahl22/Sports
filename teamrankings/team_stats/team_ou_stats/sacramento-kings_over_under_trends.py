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
driver.get("https://www.teamrankings.com/nba/team/sacramento-kings/over-under-trends")

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
            over_under_record = columns[1].text.strip()
            over_under_percent = columns[2].text.strip()
            mov = columns[3].text.strip()
            over_under_plus_minus = columns[4].text.strip()

            # Add the row data to the list
            data.append([trend, over_under_record, over_under_percent, mov, over_under_plus_minus])

    # Create a DataFrame from the data
    df = pd.DataFrame(data, columns=["Trend", "Over/Under Record", "Over/Under %", "MOV", "Over/Under +/-"])

    # Print the DataFrame (table-like format)
    print(df)

finally:
    driver.quit()  # Close the browser after scraping