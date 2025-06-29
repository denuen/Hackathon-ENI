import os
import json
from openai import OpenAI
from formatting.flushing import flush

def accumulation(json_data):
    # Inizializza il client OpenAI
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    if not os.getenv("OPENAI_API_KEY"):
        raise EnvironmentError("OPENAI_API_KEY non trovata nelle variabili d'ambiente.")

    # Gestione di diversi formati di input
    if isinstance(json_data, list):
        # Se è già una lista, usala direttamente
        documents = json_data
    elif isinstance(json_data, str):
        try:
            # Prova a convertire la stringa in lista
            documents = json.loads(json_data)
            if not isinstance(documents, list):
                print("La stringa JSON non rappresenta un array")
                return None
        except json.JSONDecodeError:
            print("Stringa JSON non valida.")
            return None
    elif isinstance(json_data, dict):
        # Se è un singolo oggetto, mettilo in una lista
        documents = [json_data]
    else:
        print(f"Formato dati non supportato: {type(json_data)}")
        return None

    # Estrai e combina i contenuti
    contenuto_completo = ""
    for doc in documents:
        # Gestione di diversi formati di documento
        if isinstance(doc, dict):
            content = doc.get("content") or doc.get("text") or doc.get("summary") or str(doc)
        elif isinstance(doc, str):
            content = doc
        else:
            content = str(doc)

        contenuto_completo += f"\n\n{content}"

    if not contenuto_completo.strip():
        print("Non sono stati trovati contenuti rilevanti")
        return None

    # Prompt migliorato con istruzioni chiare
    prompt = (
        "## ISTRUZIONI ##\n"
        "1. Analizza il seguente testo combinato da più documenti\n"
        "2. Riorganizza il contenuto evitando ripetizioni\n"
        "3. NON riassumere ulteriormente il testo\n"
        "4. Suddividi in una struttura logica con titoli e contenuti\n\n"
        "## FORMATO RICHIESTO ##\n"
        "Devi restituire SOLO un oggetto JSON con questa struttura:\n"
        "{\n"
        "  \"Titolo\": \"Titolo generale del documento\",\n"
        "  \"Sezioni\": [\n"
        "    {\"titolo\": \"Titolo sezione 1\", \"contenuto\": \"Testo sezione 1\"},\n"
        "    {\"titolo\": \"Titolo sezione 2\", \"contenuto\": \"Testo sezione 2\"}\n"
        "  ]\n"
        "}\n\n"
        "## TESTO DA ANALIZZARE ##\n"
        f"{contenuto_completo}"
    )

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "Sei un assistente che organizza documenti in strutture JSON ben formattate."
                },
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )

        result = response.choices[0].message.content

        # Validazione del risultato
        try:
            parsed_result = json.loads(result)
            if "Titolo" not in parsed_result or "Sezioni" not in parsed_result:
                print("Struttura JSON non valida nel risultato")
                return result  # Restituisci comunque il risultato grezzo
            return parsed_result
        except json.JSONDecodeError:
            print("Il modello non ha restituito JSON valido")
            return result

    except Exception as e:
        print(f"Errore nella chiamata a OpenAI: {str(e)}")
        return {"error": f"Errore nel server: {str(e)}"}
