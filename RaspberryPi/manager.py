import os
import json

script_dir = os.path.dirname(os.path.abspath(__file__))
pfad = os.path.join(script_dir, 'lager.json')

def emptySpace():
    with open(pfad, 'r') as f:
        lager = json.load(f)
        for etage in range(5):
            for fach in range(5):
                fach_id = str((etage + 1) * 10 + fach + 1)
                if lager[str(etage)][fach_id]["name"] is None:
                    return fach_id
    return None

       
def newLager():
    lager = {}

    for etage in range(5):
        etage_name = f'{etage}'
        lager[etage_name] = {}
        for fach in range(5):
            fach_id = str((etage + 1) * 10 + fach + 1)
            lager[etage_name][fach_id] = {
                'name': None,
                'beschreibung': None,
                'bild_id': None
            }

    with open('lager.json', 'w') as f:
        json.dump(lager, f, indent=2)

