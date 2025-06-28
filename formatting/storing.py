import json
import os
from datetime import datetime

STORAGE_FILE = "storico.json"

def save_in_json(toStore):
    storico = []

    # Carica file se esiste
    if os.path.exists(STORAGE_FILE):
        with open(STORAGE_FILE, "r") as f:
            try:
                storico = json.load(f)
            except json.JSONDecodeError:
                storico = []

    # Aggiungi la nuova richiesta
    storico.append(toStore)

    # Salva aggiornato
    with open(STORAGE_FILE, "w") as f:
        json.dump(storico, f, indent=4)
