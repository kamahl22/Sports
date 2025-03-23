import os
import subprocess
import time

# List of directories containing team scripts
BASE_DIRS = [
    "/Users/kamahl/Sports/scripts/nba/teamrankings/players/player_stats/nba_teams",
]

# Patterns to match player scripts in the folder
SCRIPT_PATTERNS = {
    "players/player_stats/nba_teams": "_stats_teamrankings.py",
}

def run_all_player_scripts(directories, script_patterns):
    """
    Run all Python scripts in the specified directories that match their respective patterns.
    Scripts are expected to be in player-named subdirectories within team-named subdirectories.
    
    Args:
        directories (list): List of base directory paths to process.
        script_patterns (dict): Dictionary mapping folder identifiers to script filename patterns.
    """
    total_scripts = 0
    
    for directory in directories:
        folder_key = directory.split("teamrankings/")[-1]
        pattern = script_patterns.get(folder_key, ".py")
        
        if not os.path.exists(directory):
            print(f"Error: Directory {directory} does not exist. Skipping...")
            continue
        
        print(f"\nChecking directory: {directory}")
        team_folders = [d for d in os.listdir(directory) if os.path.isdir(os.path.join(directory, d))]
        
        if not team_folders:
            print(f"No team folders found in {directory}. Directory contents:")
            print(os.listdir(directory) if os.path.exists(directory) else "Directory is empty or inaccessible.")
            continue
        
        print(f"Found {len(team_folders)} team folders: {', '.join(team_folders)}")
        
        player_scripts = []
        for team_folder in team_folders:
            team_dir = os.path.join(directory, team_folder)
            player_folders = [d for d in os.listdir(team_dir) if os.path.isdir(os.path.join(team_dir, d))]
            
            print(f"Found {len(player_folders)} player folders in {team_folder}: {', '.join(player_folders)}")
            
            for player_folder in player_folders:
                player_dir = os.path.join(team_dir, player_folder)
                files = os.listdir(player_dir)
                print(f"Contents of {team_folder}/{player_folder}/: {', '.join(files)}")
                scripts = [f for f in files if f.endswith(pattern)]
                player_scripts.extend([(team_folder, player_folder, script) for script in scripts])
        
        if not player_scripts:
            print(f"No player scripts found in {directory} matching pattern '{pattern}'.")
            continue
        
        total_scripts += len(player_scripts)
        print(f"\nFound {len(player_scripts)} player scripts in {directory}:")
        for team_folder, player_folder, script in player_scripts:
            print(f" - {team_folder}/{player_folder}/{script}")
        
        for team_folder, player_folder, script in player_scripts:
            script_path = os.path.join(directory, team_folder, player_folder, script)
            team_name = team_folder.replace('-', ' ').title()
            player_name = player_folder.replace('-', ' ').title()
            
            print(f"\nRunning script for {player_name} ({team_name}) at {team_folder}/{player_folder}/{script}...")
            try:
                start_time = time.time()
                result = subprocess.run(['python3', script_path], 
                                      capture_output=True, 
                                      text=True, 
                                      check=True)
                
                print(f"Output for {player_name} ({team_name}):")
                print(result.stdout)
                if result.stderr:
                    print(f"Errors for {player_name} ({team_name}):")
                    print(result.stderr)
                
                elapsed_time = time.time() - start_time
                print(f"Completed {script} in {elapsed_time:.2f} seconds.")
            
            except subprocess.CalledProcessError as e:
                print(f"Error running {script}:")
                print(f"Exit code: {e.returncode}")
                print(f"Output: {e.output}")
                print(f"Error: {e.stderr}")
            except Exception as e:
                print(f"Unexpected error running {script}: {e}")
            
            time.sleep(1)  # Brief pause between scripts
    
    if total_scripts == 0:
        print("\nNo scripts were found across all directories.")
    else:
        print(f"\nFinished running {total_scripts} player scripts across all directories.")

if __name__ == "__main__":
    print("Starting to run all player stats scripts across multiple directories...")
    run_all_player_scripts(BASE_DIRS, SCRIPT_PATTERNS)
    print("Execution complete.")