import os
import requests
import re

# Base directory for all team folders
base_output_dir = "nba_teams"

# Ensure the base directory exists
os.makedirs(base_output_dir, exist_ok=True)

def generate_team_script(team_id):
    # Fetch team details to get the team name
    url = f"https://site.api.espn.com/apis/site/v2/sports/basketball/nba/teams/{team_id}/roster"
    response = requests.get(url)
    data = response.json()
    
    # Extract team info
    team_info = data.get("team", {})
    team_name = team_info.get("name", f"Team_{team_id}")  # Default if name not found
    team_display_name = team_info.get("displayName", "N/A")
    team_abbreviation = team_info.get("abbreviation", "N/A")
    
    # Sanitize team name for folder and filenames (remove special characters and spaces)
    safe_team_name = re.sub(r'[^a-zA-Z0-9_-]', '_', team_name).lower()

    # Create a team-specific folder inside the base directory
    team_folder = os.path.join(base_output_dir, safe_team_name)
    os.makedirs(team_folder, exist_ok=True)  # Ensure folder exists

    # Define script content
    script_content = f"""import requests
import csv
import os

# ESPN NBA team roster API endpoint
team_id = {team_id}
url = f"https://site.api.espn.com/apis/site/v2/sports/basketball/nba/teams/{{team_id}}/roster"

# Make the API request
response = requests.get(url)
data = response.json()

# Extract team information
team_info = data.get("team", {{}})
team_name = team_info.get("name", "N/A")
team_display_name = team_info.get("displayName", "N/A")
team_abbreviation = team_info.get("abbreviation", "N/A")

# Extract players from the roster
players = data.get("athletes", [])

# Print team details
print(f"NBA Team: {{team_display_name}} ({{team_abbreviation}})")
print("=" * 40)

# Create a list for CSV output
csv_data = [("ID", "Full Name", "Display Name")]

for player in players:
    player_id = player.get("id", "N/A")
    full_name = player.get("fullName", "N/A")
    display_name = player.get("displayName", "N/A")
    
    print(f"ID: {{player_id}}")
    print(f"Full Name: {{full_name}}")
    print(f"Display Name: {{display_name}}")
    print("-" * 40)
    
    csv_data.append((player_id, full_name, display_name))

# Create team folder if it doesn't exist
team_folder = os.path.join("nba_teams", "{safe_team_name}")
os.makedirs(team_folder, exist_ok=True)

# Save data to a CSV file inside the team folder
csv_filename = os.path.join(team_folder, f"{{team_name.lower().replace(' ', '_')}}_roster.csv")

with open(csv_filename, mode="w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    writer.writerows(csv_data)

print(f"CSV file saved: {{csv_filename}}")
"""

    # Define the script path inside the team folder
    script_filename = os.path.join(team_folder, f"{safe_team_name}_roster.py")

    # Write or update the script inside the team folder
    with open(script_filename, "w") as f:
        f.write(script_content.strip())

    print(f"Script updated: {script_filename}")

# Generate a script for each team (IDs 1-30)
for team_id in range(1, 31):
    generate_team_script(team_id)