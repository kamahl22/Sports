import os
import requests
import re

# Base directory where team folders are stored
base_output_dir = "nba_teams"

# Ensure the base directory exists
if not os.path.exists(base_output_dir):
    print("Error: NBA teams directory does not exist.")
    exit()

def generate_player_script(team_folder, player_id, player_name):
    """Creates or updates a script for scraping a player's split profile from ESPN."""
    
    # Sanitize player name for folder and filenames (remove special characters and spaces)
    safe_player_name = re.sub(r'[^a-zA-Z0-9_-]', '_', player_name).lower()
    
    # Create player folder inside the team folder
    player_folder = os.path.join(team_folder, safe_player_name)
    os.makedirs(player_folder, exist_ok=True)  # Ensure folder exists

    # Player's ESPN split stats URL
    player_url = f"https://www.espn.com/nba/player/splits/_/id/{player_id}/{safe_player_name}"

    # Script content to be saved in the player's folder
    script_content = f"""import requests
import csv
import os

# Player information
player_id = {player_id}
player_name = "{player_name}"
url = "https://www.espn.com/nba/player/splits/_/id/{{player_id}}/{{player_name.lower().replace(' ', '-')}}"

# Make API request
response = requests.get(url)
if response.status_code != 200:
    print(f"Error: Unable to fetch data for {{player_name}} (ID: {{player_id}})")
    exit()

# Placeholder for parsing logic - You'll need BeautifulSoup for full scraping
data = response.text  # This will be replaced with actual parsed data

# Create CSV file inside player folder
player_folder = os.path.join("nba_teams", "{os.path.basename(team_folder)}", "{safe_player_name}")
csv_filename = os.path.join(player_folder, f"{{safe_player_name}}_splits.csv")

# Save raw data (Modify this to properly parse and extract stats)
with open(csv_filename, mode="w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    writer.writerow(["Raw HTML Data"])  # Replace with actual headers
    writer.writerow([data])  # Replace with parsed data rows

print(f"CSV file saved: {{csv_filename}}")
"""

    # Define script filename inside player's folder
    script_filename = os.path.join(player_folder, f"{safe_player_name}_splits.py")

    # Write or update the script
    with open(script_filename, "w") as f:
        f.write(script_content.strip())

    print(f"Script updated: {script_filename}")

# Loop through each team folder
for team_name in os.listdir(base_output_dir):
    team_folder = os.path.join(base_output_dir, team_name)

    # Ensure it's a directory
    if not os.path.isdir(team_folder):
        continue

    # Locate the roster CSV file
    roster_csv = None
    for file in os.listdir(team_folder):
        if file.endswith("_roster.csv"):
            roster_csv = os.path.join(team_folder, file)
            break
    
    if not roster_csv:
        print(f"No roster CSV found in {team_folder}, skipping...")
        continue

    # Read player IDs and names from the roster CSV
    with open(roster_csv, "r", encoding="utf-8") as file:
        lines = file.readlines()[1:]  # Skip header

    for line in lines:
        parts = line.strip().split(",")  # Assuming CSV format is ID, Full Name, Display Name
        if len(parts) < 2:
            continue
        
        player_id, player_name = parts[0], parts[1]  # Extract ID and full name

        # Generate the player script
        generate_player_script(team_folder, player_id, player_name)