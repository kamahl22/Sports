import time
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
url = "https://www.teamrankings.com/nba/team/indiana-pacers"
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
        print(f"Found {len(tables)} tables for Indiana Pacers. Selecting the most likely one...")

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
                df.to_csv("indiana-pacers_schedule_results.csv", index=False)
                print(f"Saved indiana-pacers_schedule_results.csv")
            else:
                print(f"Table found for Indiana Pacers, but no data extracted. Possible dynamic loading issue.")
        else:
            print(f"No matching schedule table found for Indiana Pacers.")
    else:
        print(f"No tables found for Indiana Pacers.")

except Exception as e:
    print(f"Error scraping Indiana Pacers: {e}")

# Close the browser after scraping
driver.quit()
