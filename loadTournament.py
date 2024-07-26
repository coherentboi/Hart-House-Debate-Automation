import os
import json

def load_json_data(selectedTournament):
    with open(f"{selectedTournament}/{selectedTournament}.json", "r") as file:
        loaded_data = json.load(file)
    return loaded_data

