# Script to gather player info

import requests

def get_player_stats(player_id, player_name):
    url = f"https://www.espn.com/nba/player/splits/_/id/{player_id}/{player_name}"
    
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Failed to retrieve data for {player_name} (ID: {player_id})")
        return None
    
    data = response.json()
    extracted_data = {}
    
    for category in data.get("tbl", []):
        category_name = category.get("dspNm")
        
        if category_name in ["split", "Month", "Result", "Position", "Day", "Opponent"]:
            extracted_data[category_name] = []
            
            for row in category.get("row", []):
                extracted_data[category_name].append(row[0])  # Extracting the first column value
    
    return extracted_data

# Example usage:
player_id = "4594268"  # Anthony Edwards
player_name = "anthony-edwards"
player_stats = get_player_stats(player_id, player_name)

if player_stats:
    print(player_stats)
