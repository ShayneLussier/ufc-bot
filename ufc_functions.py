import json


def save_data(fighterDict):
    # Load existing data from the file, if any
    existing_data = []
    try:
        with open("fighter_data.json", "r") as f:
            existing_data = json.load(f)
    except FileNotFoundError:
        pass

    # Append new data to the existing list of dictionaries
    existing_data.extend(fighterDict)

    # Write the updated data back to the file
    with open("fighter_data.json", "w") as file:
        json.dump(existing_data, file, indent=4)

