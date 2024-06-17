from summersplit2024 import tabs_token, tabs_link, tournament_slug, debater_information_headers,institution_column, debater_a_column, email_a_column, level_a_column, debater_b_column, email_b_column, level_b_column
from summersplit2024 import configure_break_eligibility, configure_speaker_categories 

import requests
import json

headers = {'Content-Type': 'application/json', "Authorization": f"Token {tabs_token}"}

def write_to_file(file_path, data):
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=4) 

def read_from_file(file_path):
    with open(file_path, "r") as file:
        loaded_credentials = json.load(file)
    
    return loaded_credentials

def get_institutions():
    institution_information = requests.get(tabs_link+"/institutions", headers=headers).json()
    institutions = {}
    for institution in institution_information:
        institutions[institution["name"].lower()] = institution["id"]
    write_to_file("institutions.json", institutions)

def get_break_categories():
    break_categories_information = requests.get(tabs_link+f"/tournaments/{tournament_slug}/break-categories", headers=headers).json()
    break_categories = {}
    for break_category in break_categories_information:
        break_categories[break_category["name"]] = break_category["id"]
    write_to_file("break-categories.json", break_categories)

def get_speaker_categories():
    speaker_categories_information = requests.get(tabs_link+f"/tournaments/{tournament_slug}/speaker-categories", headers=headers).json()
    speaker_categories = {}
    for speaker_category in speaker_categories_information:
        speaker_categories[speaker_category["name"]] = speaker_category["id"]
    write_to_file("speaker-categories.json", speaker_categories)

def get_teams():
    response = requests.get(tabs_link+f"/tournaments/{tournament_slug}/teams", headers=headers)
    if(response.status_code == 200):
        print("Teams Extracted Successfully")
    else:
        print("Team Extraction Failed", response.status_code)
    write_to_file("teams.json", response.json())

def check_team(data):
    get_teams()
    teams = read_from_file("teams.json")
    for team in teams:
        if(team["long_name"] == data["reference"]):
            print(f"Team Already Exists")
            return True
    return False

def create_team(data):
    if check_team(data):
        return False
    
    response = requests.post(tabs_link+f"/tournaments/{tournament_slug}/teams", headers=headers, data=json.dumps(data))
    if(response.status_code == 200 or response.status_code == 201):
        print(f"Team {data['reference']} Created Successfully")
    else:
        print(f"Team {data['reference']} Creation Failed", response.status_code)

    get_teams()

    return response.json()

def create_speaker(data):
    response = requests.post(tabs_link+f"/tournaments/{tournament_slug}/speakers", headers=headers, data=json.dumps(data))
    if(response.status_code == 200 or response.status_code == 201):
        print(f"Speaker {data['name']} Created Successfully")
    else:
        print(f"Speaker {data['name']} Creation Failed", response.status_code, response.json())

def create_institution(data):
    response = requests.post(tabs_link+f"/institutions", headers=headers, data=json.dumps(data))
    if(response.status_code == 200 or response.status_code == 201):
        print("Institution Created Successfully")
    else:
        print("Institution Creation Failed", response.status_code)
    return response.json()

def create_teams(team_data, team_names):
    columns = []
    for header in debater_information_headers:
        columns.append(team_data[0].index(header))
    institutions = read_from_file("institutions.json")
    if(len(team_names) < len(team_data) - 1):
        print("Not enough team names! Please add more!")
        return
    for index, team in enumerate(team_data[1:]):
        creation_data = {}
        institution_name = team[institution_column]
        if(institution_name.lower() not in institutions.keys()):
            create_institution({"name": institution_name, "code": institution_name})
            get_institutions()
            institutions = read_from_file("institutions.json")
        creation_data["institution"] = tabs_link+f"/institutions/{institutions[institution_name.lower()]}"
        creation_data["break_categories"] = configure_break_eligibility(team)
        creation_data["reference"] = team_names[index][0]
        creation_data["short_reference"] = team_names[index][0]

        team_info = create_team(creation_data)

        if team_info == False:
            continue
        
        speaker_a_data = {"name": team[debater_a_column], "email": team[email_a_column], "team": team_info["url"], "categories": configure_speaker_categories(team[level_a_column])}
        speaker_b_data = {"name": team[debater_b_column], "email": team[email_b_column], "team": team_info["url"], "categories": configure_speaker_categories(team[level_b_column])}

        create_speaker(speaker_a_data)
        create_speaker(speaker_b_data)



