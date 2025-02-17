import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
from sklearn.preprocessing import StandardScaler

# Scraping function to gather win-trends data
def scrape_team_data(url):
    options = Options()
    options.headless = True
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    driver.get(url)
    time.sleep(5)  # Wait for the page to load
    
    # Wait for the table to load
    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.XPATH, '//table[contains(@class, "tr-table")]'))
    )
    
    # Extract data
    data = []
    rows = driver.find_elements(By.XPATH, '//table[contains(@class, "tr-table")]/tbody/tr')
    
    for row in rows:
        cols = row.find_elements(By.TAG_NAME, 'td')
        if len(cols) > 0:
            trend = cols[0].text.strip()
            record = cols[1].text.strip()
            cover_percent = cols[2].text.strip()
            mov = cols[3].text.strip()
            ats_plus_minus = cols[4].text.strip()
            data.append([trend, record, cover_percent, mov, ats_plus_minus])
    
    driver.quit()
    
    # Convert data to DataFrame
    df = pd.DataFrame(data, columns=["Trend", "Record", "Cover %", "MOV", "ATS +/-"])
    
    return df

# URLs for Grizzlies and Pacers
grizzlies_url = "https://www.teamrankings.com/nba/team/memphis-grizzlies/win-trends"
pacers_url = "https://www.teamrankings.com/nba/team/indiana-pacers/win-trends"

# Scrape data for both teams
grizzlies_data = scrape_team_data(grizzlies_url)
pacers_data = scrape_team_data(pacers_url)

# Combine both teams' data
grizzlies_data['Team'] = 'Grizzlies'
pacers_data['Team'] = 'Pacers'
combined_data = pd.concat([grizzlies_data, pacers_data])

# For simplicity, we use win trend data and the "Cover %" to predict the winner
# We'll create a simple binary target where 1 indicates a win and 0 indicates a loss
# We can assume the first few rows indicate wins/losses, but this will be improved with more complex logic

combined_data['Winner'] = combined_data['Trend'].apply(lambda x: 1 if 'win' in x.lower() else 0)

# Prepare features (X) and target (y)
X = combined_data[['Cover %', 'MOV', 'ATS +/-']]  # Example features
y = combined_data['Winner']  # Target: Winner (binary)

# Preprocess: Convert percentages to numeric and handle any missing values
X = X.replace('%', '', regex=True).apply(pd.to_numeric, errors='coerce')
X.fillna(X.mean(), inplace=True)

# Split data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

# Standardize the data (optional but helps models like Random Forest)
scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)

# Train a Random Forest Classifier
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Predict on test set
y_pred = model.predict(X_test)

# Evaluate the model
accuracy = accuracy_score(y_test, y_pred)
print(f'Model Accuracy: {accuracy * 100:.2f}%')

# Now you can predict the winner for the next match based on this model
# Example prediction for new data
new_game = pd.DataFrame({
    'Cover %': [50],  # Example value, replace with real stats
    'MOV': [5],       # Example value
    'ATS +/-': [1]    # Example value
})

new_game = scaler.transform(new_game)
predicted_winner = model.predict(new_game)

print("Predicted Winner: Grizzlies" if predicted_winner[0] == 1 else "Predicted Winner: Pacers")