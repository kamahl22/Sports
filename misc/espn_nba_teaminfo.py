# Script to fetch team ID, team name, team abbreviation

import requests

# ESPN NBA teams API endpoint
url = "http://site.api.espn.com/apis/site/v2/sports/basketball/nba/teams"

# Make the API request
response = requests.get(url)
data = response.json()

# Extract all NBA teams
teams = data["sports"][0]["leagues"][0]["teams"]

# Print each team's ID, slug, and abbreviation
for team in teams:
    team_data = team["team"]
    print(f"ID: {team_data['id']}")
    print(f"Slug: {team_data['slug']}")
    print(f"Abbreviation: {team_data['abbreviation']}")
    print()