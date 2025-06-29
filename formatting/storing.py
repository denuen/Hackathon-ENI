import json
import os
from datetime import datetime

STORAGE_FILE = "storico.json"

def store_answer(toStore):
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

def get_stored_documents():
    """Recupera tutti i documenti salvati nel file storico"""
    if os.path.exists(STORAGE_FILE):
        try:
            with open(STORAGE_FILE, "r") as f:
                return json.load(f)
        except json.JSONDecodeError:
            return []
    return []
