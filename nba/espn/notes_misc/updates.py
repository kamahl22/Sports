import os

# Create output directory for team scripts
output_dir = "nba_team_rosters"
os.makedirs(output_dir, exist_ok=True)

def generate_team_script(team_id):
    script_content = f"""import requests

# ESPN NBA team roster API endpoint
team_id = {team_id}
url = f"https://site.api.espn.com/apis/site/v2/sports/basketball/nba/teams/{{team_id}}/roster"

# Make the API request
response = requests.get(url)
data = response.json()

# Extract players from the roster
players = data.get("athletes", [])

# Print organized player information
print(f"NBA Team Roster (Team ID: {{team_id}})")
print("=" * 40)

for player in players:
    player_id = player.get("id", "N/A")
    full_name = player.get("fullName", "N/A")
    display_name = player.get("displayName", "N/A")
    
    print(f"ID: {{player_id}}")
    print(f"Full Name: {{full_name}}")
    print(f"Display Name: {{display_name}}")
    print("-" * 40)
"""

    script_filename = os.path.join(output_dir, f"team_{team_id}_roster.py")
    with open(script_filename, "w") as f:
        f.write(script_content.strip())

    print(f"Script generated: {script_filename}")

# Generate a script for each team (IDs 1-30)
for team_id in range(1, 31):
    generate_team_script(team_id)