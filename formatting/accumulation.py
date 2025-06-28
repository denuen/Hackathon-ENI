import os
import json
import openai

def accumulation(json_string):
    openai.api_key = os.getenv("OPENAI_API_KEY")
    if not openai.api_key:
        raise EnvironmentError("OPENAI_API_KEY non trovata nelle variabili d'ambiente.")

    contenuto_completo = ""

    try:
        data = json.loads(json_string)
    except json.JSONDecodeError:
        print("Stringa JSON non valida.")
        return

    if not data:
        print("Non sono stati trovati contenuti rilevanti")
        return

    content = data.get("content")

    if content is None:
        print("Chiave 'content' mancante")
        return

    contenuto_completo += content + "\n\n"

    prompt = f"Ecco un testo da analizzare: \n {contenuto_completo}\n Riorganizza il contenuto evitando ripetizioni, evita assolutamente di riassumere ancora di più il testo, e suddividilo in titoli e contenuti.\n Restituisci la risposta in formato JSON come array di oggetti, ciascuno con i campi 'title' e 'content', senza testo aggiuntivo."
    
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        return (response["choices"][0]["message"]["content"])
    except Exception as e:
        return ("Errore nel server", str(e))
