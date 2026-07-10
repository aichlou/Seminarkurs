import os
import json

script_dir = os.path.dirname(os.path.abspath(__file__))
pfad = os.path.join(script_dir, 'lager.json')

def emptySpace():
    with open(pfad, 'r') as f:
        lager = json.load(f)

    best_fach_id = None
    best_quersumme = None

    for etage in range(5):
        for fach in range(5):
            fach_id = str((etage + 1) * 10 + fach + 1)
            if lager[str(etage)][fach_id]["name"] is None:
                quersumme = sum(int(digit) for digit in fach_id)
                if best_quersumme is None or quersumme < best_quersumme or (
                    quersumme == best_quersumme and int(fach_id) < int(best_fach_id)
                ):
                    best_quersumme = quersumme
                    best_fach_id = fach_id

    return best_fach_id

_UNSET = object()

def bearbeite_fach(fach_id, name=_UNSET, beschreibung=_UNSET, bild_id=_UNSET):
    global pfad
    with open(pfad, 'r') as f:
        lager = json.load(f)
    fach_id = str(fach_id)

    ziel_etage = None
    for etage_name, faecher in lager.items():
        if fach_id in faecher:
            ziel_etage = etage_name
            break

    if ziel_etage is None:
        raise KeyError(f"Fach_ID '{fach_id}' wurde in keiner Etage gefunden.")

    fach = lager[ziel_etage][fach_id]

    if name is not _UNSET:
        fach['name'] = name
    if beschreibung is not _UNSET:
        fach['beschreibung'] = beschreibung
    if bild_id is not _UNSET:
        fach['bild_id'] = bild_id
        
    with open(pfad, 'w', encoding='utf-8') as f:
        json.dump(lager, f, indent=2, ensure_ascii=False)


def alleItems():
    with open(pfad, 'r') as f:
        lager = json.load(f)

    items = {}
    for etage_name, etage in lager.items():
        for fach_id, fach in etage.items():
            if fach.get('name') is not None:
                items[fach_id] = {
                    'name': fach['name'],
                    'beschreibung': fach.get('beschreibung'),
                    'position': fach_id
                }

    if not items:
        return {'0': 'Kein Inhalt'}
    return items   

       
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

