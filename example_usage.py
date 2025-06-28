import os
import sys
from pathlib import Path

# Aggiungi il percorso del progetto al sys.path per gli import
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from ingest.extractor import Ingest


def main():
    """
    Esempio di utilizzo del modulo extractor.
    """
    # Definisci le directory di input e output
    input_directory = os.path.join(project_root, "input")
    output_directory = os.path.join(project_root, "output")

    print("=== Knowledge Capture - Estrazione Contenuti ===")
    print(f"Directory input: {input_directory}")
    print(f"Directory output: {output_directory}")

    # Verifica che la directory di input esista
    if not os.path.exists(input_directory):
        print(f"Creando directory di input: {input_directory}")
        os.makedirs(input_directory, exist_ok=True)
        print("La directory input è vuota. Aggiungi file da processare e riavvia lo script.")
        return

    # Verifica se ci sono file da processare
    files = [f for f in os.listdir(input_directory) if os.path.isfile(os.path.join(input_directory, f))]
    if not files:
        print("Nessun file trovato nella directory input.")
        return

    print(f"Trovati {len(files)} file da processare:")
    for file in files[:5]:  # Mostra solo i primi 5 file
        print(f"  - {file}")
    if len(files) > 5:
        print(f"  ... e altri {len(files) - 5} file")

    try:
        # Avvia il processo di ingestione
        print("\nAvvio del processo di ingestione...")
        Ingest(input_directory, output_directory)
        print("\n✓ Processo completato con successo!")

    except Exception as e:
        print(f"\n✗ Errore durante l'ingestione: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
