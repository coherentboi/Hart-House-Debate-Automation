import os
import json

def load_tournaments():
    with open("./tournaments/tournaments.json", "r") as file:
        tournaments = json.load(file)["tournaments"]
    return tournaments

def load_tournament_data(selectedTournament):
    with open(f"./tournaments/{selectedTournament}/{selectedTournament}.json", "r") as file:
        loaded_data = json.load(file)
    return loaded_data

