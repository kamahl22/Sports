import os
import subprocess
import time

# List of directories containing team scripts
BASE_DIRS = [
    # "/Users/kamahl/Sports/scripts/nba/teamrankings/team_stats/team_ats_stats/nba_teams",
    # "/Users/kamahl/Sports/scripts/nba/teamrankings/team_stats/team_win_stats",
    # "/Users/kamahl/Sports/scripts/nba/teamrankings/team_stats/team_ou_stats/nba_teams",
    # "/Users/kamahl/Sports/scripts/nba/teamrankings/team_stats/team_overall_stats/nba_teams",
    # Add other directories as needed
    # "/Users/kamahl/Sports/scripts/nba/teamrankings/players/roster/nba_teams",
    "/Users/kamahl/Sports/scripts/nba/teamrankings/players/player_stats/nba_teams",
    # "/Users/kamahl/Sports/scripts/nba_rosters_and_stats/teamrankings/win_trends/teams"
]

# Patterns to match team scripts in each folder
SCRIPT_PATTERNS = {
    "team_stats/team_ats_stats/nba_teams": "_ats_trends.py",  # Fixed to match actual filenames
    "team_stats/team_win_stats/nba_teams": "_win_trends.py",
    "team_stats/team_overall_stats/teams": "_team_stats.py",
    "ats_trends/teams": "_ats_trends.py",
    "over_under_trends/teams": "_over_under_trends.py",
    "win_trends/teams": "_win_trends.py"
}

def run_all_team_scripts(directories, script_patterns):
    """
    Run all Python scripts in the specified directories that match their respective patterns.
    Scripts are expected to be in team-named subdirectories.
    
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
        
        team_scripts = []
        for team_folder in team_folders:
            team_dir = os.path.join(directory, team_folder)
            files = os.listdir(team_dir)
            print(f"Contents of {team_folder}/: {', '.join(files)}")
            scripts = [f for f in files if f.endswith(pattern) and f not in ['nba_teams_ats.py', 'nba_teams_wins.py', 'nba_teams_ou.py', 'generate_team_stats_scripts.py']]
            team_scripts.extend([(team_folder, script) for script in scripts])
        
        if not team_scripts:
            print(f"No team scripts found in {directory} matching pattern '{pattern}'.")
            continue
        
        total_scripts += len(team_scripts)
        print(f"\nFound {len(team_scripts)} team scripts in {directory}:")
        for team_folder, script in team_scripts:
            print(f" - {team_folder}/{script}")
        
        for team_folder, script in team_scripts:
            script_path = os.path.join(directory, team_folder, script)
            team_name = team_folder.replace('-', ' ').title()
            
            print(f"\nRunning script for {team_name} ({team_folder}/{script}) in {directory}...")
            try:
                start_time = time.time()
                result = subprocess.run(['python3', script_path], 
                                      capture_output=True, 
                                      text=True, 
                                      check=True)
                
                print(f"Output for {team_name}:")
                print(result.stdout)
                if result.stderr:
                    print(f"Errors for {team_name}:")
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
            
            time.sleep(1)
    
    if total_scripts == 0:
        print("\nNo scripts were found across all directories.")
    else:
        print(f"\nFinished running {total_scripts} team scripts across all directories.")

if __name__ == "__main__":
    print("Starting to run all team scripts across multiple directories...")
    run_all_team_scripts(BASE_DIRS, SCRIPT_PATTERNS)
    print("Execution complete.")