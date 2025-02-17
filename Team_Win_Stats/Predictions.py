import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import numpy as np
from webdriver_manager.chrome import ChromeDriverManager

# Set up the ChromeDriver
options = Options()
options.headless = False  # Set to True if you want to run it in headless mode
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# List of NBA teams and their slug names for scraping
nba_teams = [
    "chicago-bulls","golden-state-warriors"
]

# Function to scrape ATS, O/U, and Win data for each team
def scrape_team_data(team_slug):
    driver.get(f"https://www.teamrankings.com/nba/team/{team_slug}/ats-trends")
    time.sleep(5)

    # Extract data
    data = []
    try:
        # Scrape the ATS trends table
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, '//table[contains(@class, "tr-table")]'))
        )
        table = driver.find_element(By.XPATH, '//table[contains(@class, "tr-table")]')
        rows = table.find_elements(By.TAG_NAME, "tr")
        
        for row in rows:
            columns = row.find_elements(By.TAG_NAME, "td")
            if len(columns) >= 5:
                trend = columns[0].text.strip()
                ats_record = columns[1].text.strip()
                cover_percent = columns[2].text.strip()
                mov = columns[3].text.strip()
                ats_plus_minus = columns[4].text.strip()

                data.append([trend, ats_record, cover_percent, mov, ats_plus_minus])
    except Exception as e:
        print(f"Error scraping {team_slug}: {e}")

    return data

# Collect data for each team
team_data = []
for team_slug in nba_teams:
    team_stats = scrape_team_data(team_slug)
    if team_stats:
        team_data.extend(team_stats)

# Create a DataFrame from the scraped data
df = pd.DataFrame(team_data, columns=["Trend", "ATS Record", "Cover %", "MOV", "ATS +/-"])

# Clean and process the data
df['Cover %'] = df['Cover %'].str.replace('%', '').astype(float) / 100
df['MOV'] = df['MOV'].astype(float)
df['ATS +/-'] = df['ATS +/-'].astype(float)

# Features and labels for prediction
# For simplicity, we'll predict if a team covers the spread based on their performance
df['Cover Prediction'] = df['Cover %'] > 0.5  # If cover percentage is above 50%, they are likely to cover

# Convert categorical trend information to numerical encoding for model input
df['Trend'] = df['Trend'].apply(lambda x: 1 if 'home' in x.lower() else (0 if 'away' in x.lower() else 2))

# Selecting features and target
X = df[['Trend', 'Cover %', 'MOV', 'ATS +/-']]
y = df['Cover Prediction']

# Split the data into training and test sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train a simple Random Forest model for prediction
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Test the model and evaluate its accuracy
y_pred = model.predict(X_test)
print(f"Accuracy: {accuracy_score(y_test, y_pred):.2f}")

# Now, make predictions for the next game for each team
def predict_game_outcome(team_data_row):
    trend, cover_percentage, mov, ats_plus_minus = team_data_row
    features = np.array([[trend, cover_percentage, mov, ats_plus_minus]])
    prediction = model.predict(features)
    return "Cover" if prediction[0] else "Not Cover"

# Example prediction for the first team
team_example = df.iloc[0]
prediction = predict_game_outcome(team_example[['Trend', 'Cover %', 'MOV', 'ATS +/-']].values)
print(f"Prediction for the next game (ATS): {prediction}")

# Close the driver after scraping
driver.quit()