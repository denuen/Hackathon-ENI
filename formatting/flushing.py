import os
import json

def flush(json_string):
    try:
        data = json.loads(json_string)
    except json.JSONDecodeError:
        print("Stringa JSON non valida")
        return

    if not isinstance(data, list):
        print("Errore: non è una lista")
        return

    for item in data:
        title = item.get("title")
        content = item.get("content")
        print(f"TITOLO: {title}")
        print(f"CONTENUTO: {content}")
        print("------")
    
    store_answer(data)

#the content is still a print for a reason of the test, in the actual output it's going to added to the visualization