import requests
import json

from openAIUtil import createInstitutionCode

def write_to_file(file_path, data):
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=4) 

def read_from_file(file_path):
    with open(file_path, "r") as file:
        loaded_credentials = json.load(file)
    
    return loaded_credentials

def get_institutions(config, headers):
    institution_information = requests.get(config['tabs_link']+"/institutions", headers=headers).json()
    institutions = {}
    for institution in institution_information:
        institutions[institution["name"].lower()] = institution["id"]
    write_to_file(f"{config['tournament_name']}/institutions.json", institutions)

def get_break_categories(config, headers):
    break_categories_information = requests.get(config['tabs_link']+f"/tournaments/{config['tournament_slug']}/break-categories", headers=headers).json()
    break_categories = {}
    for break_category in break_categories_information:
        break_categories[break_category["name"]] = break_category["id"]
    write_to_file(f"{config['tournament_name']}/break-categories.json", break_categories)

def get_speaker_categories(config, headers):
    speaker_categories_information = requests.get(config['tabs_link']+f"/tournaments/{config['tournament_slug']}/speaker-categories", headers=headers).json()
    speaker_categories = {}
    for speaker_category in speaker_categories_information:
        speaker_categories[speaker_category["name"]] = speaker_category["id"]
    write_to_file(f"{config['tournament_name']}/speaker-categories.json", speaker_categories)

def get_teams(config, headers):
    response = requests.get(config['tabs_link']+f"/tournaments/{config['tournament_slug']}/teams", headers=headers)
    if(response.status_code == 200):
        print("Teams Extracted Successfully")
    else:
        print("Team Extraction Failed", response.status_code)
    write_to_file(f"{config['tournament_name']}/teams.json", response.json())

def check_team(config, headers, data):
    get_teams(config, headers)
    teams = read_from_file(f"{config['tournament_name']}/teams.json")
    for team in teams:
        if(team["long_name"] == data["reference"]):
            print(f"Team Already Exists")
            return True
    return False

def create_team(config, headers, data):
    if check_team(config, headers, data):
        return False
    
    response = requests.post(config['tabs_link']+f"/tournaments/{config['tournament_slug']}/teams", headers=headers, data=json.dumps(data))
    if(response.status_code == 200 or response.status_code == 201):
        print(f"Team {data['reference']} Created Successfully")
    else:
        print(f"Team {data['reference']} Creation Failed", response.status_code)

    get_teams(config, headers)

    return response.json()

def create_speaker(config, headers, data):
    response = requests.post(config['tabs_link']+f"/tournaments/{config['tournament_slug']}/speakers", headers=headers, data=json.dumps(data))
    if(response.status_code == 200 or response.status_code == 201):
        print(f"Speaker {data['name'].title()} Created Successfully")
    else:
        print(f"Speaker {data['name'].title()} Creation Failed", response.status_code, response.json())

def create_institution(config, headers, name):
    code = createInstitutionCode(name)
    response = requests.post(config['tabs_link']+f"/institutions", headers=headers, data=json.dumps({"name": name, "code": code}))
    if(response.status_code == 200 or response.status_code == 201):
        print(f"Institution {name}, {code} Created Successfully")
    else:
        print("Institution Creation Failed", response.status_code)
    return response.json()

def configure_break_eligibility(config, team):
    print(team)
    return config["break_categories"]

def configure_speaker_categories(config, level):
    categories = []
    if(level in config["speaker_categories"]):
        categories.extend(config["speaker_categories"][level])
    categories.extend(config["speaker_categories"]["default"])
    return categories

def create_teams(config, headers, team_data, team_names):
    columns = []
    for header in config["debater_information_headers"]:
        columns.append(team_data[0].index(header))
    institutions = read_from_file(f"{config['tournament_name']}/institutions.json")
    if(len(team_names) < len(team_data) - 1):
        print("Not enough team names! Please add more!")
        return
    for index, team in enumerate(team_data[1:]):
        creation_data = {}
        institution_name = team[config["institution_column"]]
        if(institution_name.lower() not in institutions.keys()):
            create_institution(config, headers, institution_name)
            get_institutions(config, headers)
            institutions = read_from_file(f"{config['tournament_name']}/institutions.json")
        creation_data["institution"] = config['tabs_link']+f"/institutions/{institutions[institution_name.lower().strip()]}"
        creation_data["break_categories"] = configure_break_eligibility(config, team)
        creation_data["reference"] = team_names[index][0]
        creation_data["short_reference"] = team_names[index][0]

        team_info = create_team(config, headers, creation_data)

        if team_info == False:
            continue
        
        speaker_a_data = {"name": team[config["debater_a_column"]].title(), "email": team[config["email_a_column"]], "team": team_info["url"], "categories": configure_speaker_categories(config, team[config["level_a_column"]])}
        speaker_b_data = {"name": team[config["debater_b_column"]].title(), "email": team[config["email_b_column"]], "team": team_info["url"], "categories": configure_speaker_categories(config, team[config["level_b_column"]])}

        create_speaker(config, headers, speaker_a_data)
        create_speaker(config, headers, speaker_b_data)



