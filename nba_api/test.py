from nba_api.stats.static import teams
from nba_api.stats.static import players

# get_teams returns a list of 30 dictionaries, each an NBA team.
nba_teams = teams.get_teams()
print("Number of teams fetched: {}".format(len(nba_teams)))
nba_teams[:3]

# get_players returns a list of dictionaries, each representing a player.
nba_players = players.get_players()
print("Number of players fetched: {}".format(len(nba_players)))
nba_players[:5]

spurs = [team for team in nba_teams if team["full_name"] == "San Antonio Spurs"][0]
print(spurs)

big_fundamental = [
    player for player in nba_players if player["full_name"] == "Tim Duncan"
][0]
print(big_fundamental)