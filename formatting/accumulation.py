import os
import json
import logging
from openai import OpenAI
from formatting.flushing import flush

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def accumulation(json_data, keywords=None):
    logger.info(f"Accumulation chiamata con keywords: {keywords}")

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

    # Costruisci il contesto delle keywords
    keywords_context = ""
    if keywords and len(keywords) > 0:
        keywords_text = ", ".join(keywords)
        keywords_context = f"""
## FOCUS TEMATICO ##
TEMI DI INTERESSE: {keywords_text}

ISTRUZIONI:
- Dai priorità alle informazioni correlate a questi temi nell'organizzazione del contenuto
- Crea una struttura logica e armonica del documento
- Utilizza titoli di sezione naturali e descrittivi (NON le keywords letterali)
- Mantieni il flusso narrativo e la coerenza del documento
- Assicurati che i temi richiesti siano ben rappresentati nel documento finale"""

    # Prompt migliorato con istruzioni chiare
    prompt_base = """## ISTRUZIONI PRINCIPALI ##
1. Analizza il seguente testo combinato da più documenti
2. Organizza il contenuto in un documento ben strutturato e armonico
3. Crea sezioni logiche con titoli naturali e descrittivi
4. Mantieni il flusso narrativo e la coerenza del testo
5. Evita ripetizioni e ridondanze
6. Assicurati che il documento sia facilmente comprensibile
7. Usa una strutturazione professionale e chiara"""

    if keywords and len(keywords) > 0:
        prompt_instructions = f"""
## PRIORITÀ TEMATICHE ##
- Dai particolare attenzione alle informazioni sui temi: {", ".join(keywords)}
- Assicurati che questi argomenti siano ben rappresentati nel documento finale
- Organizza il contenuto in modo che i temi richiesti emergano chiaramente
- Mantieni comunque una struttura logica e naturale del documento
- I titoli delle sezioni devono essere descrittivi e professionali, non le keywords letterali"""
    else:
        prompt_instructions = """
## APPROCCIO GENERALE ##
- Suddividi in sezioni logiche basate sui contenuti principali
- Mantieni una struttura chiara e organizzata
- Crea titoli di sezione naturali e descrittivi"""

    prompt = (
        prompt_base +
        prompt_instructions +
        keywords_context +
        "\n\n## FORMATO RICHIESTO ##\n"
        "Devi restituire SOLO un oggetto JSON con questa struttura:\n"
        "{\n"
        "  \"Titolo\": \"Titolo professionale che riflette il contenuto del documento\",\n"
        "  \"Sezioni\": [\n"
        "    {\"titolo\": \"Titolo sezione naturale e descrittivo\", \"contenuto\": \"Contenuto dettagliato della sezione\"},\n"
        "    {\"titolo\": \"Altro titolo sezione professionale\", \"contenuto\": \"Contenuto dettagliato della sezione\"}\n"
        "  ]\n"
        "}\n\n"
        "IMPORTANTE: I titoli delle sezioni devono essere naturali, professionali e descrittivi del contenuto, NON le keywords letterali.\n\n"
        "## TESTO DA ANALIZZARE ##\n"
        f"{contenuto_completo}"
    )

    logger.info("Invio richiesta a OpenAI per accumulation...")
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "Sei un assistente specializzato nella creazione di documenti ben strutturati e armoniosi. Organizzi il contenuto in sezioni logiche e naturali, mantenendo un flusso narrativo chiaro e professionale. Crei titoli descrittivi e naturali per le sezioni."
                },
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            timeout=60  # Timeout di 60 secondi
        )

        logger.info("Risposta ricevuta da OpenAI")
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
