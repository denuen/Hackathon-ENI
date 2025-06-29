import os
import sys
import json
import asyncio
from pathlib import Path

# Aggiungi la cartella 'summarize' al percorso di sistema
sys.path.insert(0, str(Path(__file__).parent / "summarize"))

# Ora possiamo importare il Chunker
from chunker import Chunker, ChunkerConfig

# Importa l'ingest dalla cartella ingest
from ingest.extractor import Ingest

# Imposta il percorso della directory del progetto
project_root = Path(__file__).parent

def main():
    # Directory di input
    input_dir = project_root / "input"
    # Directory di output per l'ingest
    ingest_output_dir = project_root / "output" / "ingest"
    # Directory di output per il summarization
    summary_output_dir = project_root / "output" / "summary"

    print(f"Input directory: {input_dir}")
    print(f"Ingest output: {ingest_output_dir}")
    print(f"Summary output: {summary_output_dir}")

    # Crea le directory se non esistono
    input_dir.mkdir(exist_ok=True, parents=True)
    ingest_output_dir.mkdir(exist_ok=True, parents=True)
    summary_output_dir.mkdir(exist_ok=True, parents=True)

    # Verifica presenza file nella directory di input
    input_files = [f for f in input_dir.iterdir() if f.is_file()]
    
    if not input_files:
        print("Nessun file trovato nella directory di input")
        return

    print(f"{len(input_files)} file trovati:")
    for file in input_files:
        print(f"  - {file.name}")

    try:
        # Fase 1: Esecuzione dell'ingest
        print("\n[FASE 1] Avvio processo di ingest...")
        Ingest(str(input_dir), str(ingest_output_dir))
        print("Ingest completato con successo!")
        
        # Carica i file prodotti dall'ingest (file JSON)
        ingest_files = list(ingest_output_dir.glob("*.json"))
        
        if not ingest_files:
            print("Nessun file prodotto dall'ingest")
            return
            
        print(f"\n{len(ingest_files)} file prodotti dall'ingest:")
        ingested_docs = []
        for json_file in ingest_files:
            with open(json_file, 'r', encoding='utf-8') as f:
                doc_data = json.load(f)
                ingested_docs.append(doc_data)
                print(f"  - {json_file.name} caricato")

        # Fase 2: Esecuzione del summarization
        print("\n[FASE 2] Avvio processo di summarization...")
        chunker_cfg = ChunkerConfig(
            max_tokens=1024,
            handle_audio_video=True,
            model_map="gpt-4o",
            model_reduce="gpt-4o",
            max_concurrency=5
        )
        chunker = Chunker(chunker_cfg)
        summarized_docs = asyncio.run(chunker.process_documents(ingested_docs))
        print(f"Summarization completato! {len(summarized_docs)} documenti elaborati")


        # Salva i risultati del summarization
        print("\nSalvataggio risultati del summarization...")
        for i, doc in enumerate(summarized_docs):
            output_file = summary_output_dir / f"summary_{i}.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(doc, f, indent=2, ensure_ascii=False)
            print(f"  - Salvato: {output_file}")
        
        print("\nElaborazione completata con successo!")
        
        # Esegui la tua funzione con l'output del summarization
	accumulated_summarizes = accumulation(summarized_docs)
	flush(accumulated_summarizes)

    except Exception as e:
        print(f"\nERRORE durante l'elaborazione: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()