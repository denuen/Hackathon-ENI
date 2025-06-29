import os
import sys
import json
import asyncio
from pathlib import Path
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename
import tempfile
import shutil
from dotenv import load_dotenv

# Carica le variabili d'ambiente dal file .env
load_dotenv()

# Aggiungi la cartella 'summarize' al percorso di sistema
sys.path.insert(0, str(Path(__file__).parent / "summarize"))
sys.path.insert(0, str(Path(__file__).parent / "formatting"))

# Importa le dipendenze necessarie
from chunker import Chunker, ChunkerConfig
from ingest.extractor import Ingest
from formatting.accumulation import accumulation
from formatting.storing import store_answer, get_stored_documents

app = Flask(__name__)

# Configurazione CORS più esplicita
CORS(app, resources={
    r"/api/*": {
        "origins": ["http://localhost:5173", "http://localhost:3000", "http://127.0.0.1:5173"],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

# Configurazione
app.config['MAX_CONTENT_LENGTH'] = 100 * 5000 * 2048  # 100MB max file size
UPLOAD_FOLDER = Path(__file__).parent / "input"
OUTPUT_FOLDER = Path(__file__).parent / "output"
ALLOWED_EXTENSIONS = {'pdf', 'txt', 'doc', 'docx', 'odt', 'rtf',
	'ppt', 'pptx', 'odp', 'xlsx', 'xls', 'ods', 'csv',
	'xml', 'json','jpg', 'jpeg', 'png', 'bmp', 'tiff', 'tif',
	'gif', 'webp', 'svg', 'csv', 'mp3', 'wav', 'm4a', 'aac', 'flac', 'ogg',
	'wma', 'amr', 'opus', 'mov', 'mp4', 'avi', 'mkv', 'wmv', 'webm', 'm4v',
	'flv', '3gp', 'mpg', 'mpeg'}

# Crea le directory necessarie
UPLOAD_FOLDER.mkdir(exist_ok=True, parents=True)
(OUTPUT_FOLDER / "ingest").mkdir(exist_ok=True, parents=True)
(OUTPUT_FOLDER / "summary").mkdir(exist_ok=True, parents=True)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/api/health', methods=['GET'])
def health_check():
    """Endpoint per verificare che il server sia attivo"""
    return jsonify({"status": "ok", "message": "Server is running"})

@app.route('/api/upload', methods=['POST'])
def upload_files():
    """Endpoint per l'upload e l'elaborazione dei file"""
    try:
        if 'files' not in request.files:
            return jsonify({"error": "Nessun file fornito"}), 400

        files = request.files.getlist('files')

        if not files or all(f.filename == '' for f in files):
            return jsonify({"error": "Nessun file selezionato"}), 400

        uploaded_files = []

        # Salva i file uploadati
        for file in files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file_path = UPLOAD_FOLDER / filename
                file.save(str(file_path))
                uploaded_files.append(filename)
            else:
                return jsonify({"error": f"Tipo di file non supportato: {file.filename}"}), 400

        # Elabora i file
        result = process_files()

        return jsonify({
            "message": "File caricati ed elaborati con successo",
            "uploaded_files": uploaded_files,
            "processing_result": result
        })

    except Exception as e:
        return jsonify({"error": f"Errore durante l'elaborazione: {str(e)}"}), 500

def process_files():
    """Elabora i file caricati attraverso il pipeline di ingest e summarization"""
    try:
        # Directory
        input_dir = UPLOAD_FOLDER
        ingest_output_dir = OUTPUT_FOLDER / "ingest"
        summary_output_dir = OUTPUT_FOLDER / "summary"

        # Verifica presenza file
        input_files = [f for f in input_dir.iterdir() if f.is_file()]

        if not input_files:
            return {"error": "Nessun file da elaborare"}

        # Fase 1: Ingest
        Ingest(str(input_dir), str(ingest_output_dir))

        # Carica i file prodotti dall'ingest
        ingest_files = list(ingest_output_dir.glob("*.json"))

        if not ingest_files:
            return {"error": "Nessun file prodotto dall'ingest"}

        ingested_docs = []
        for json_file in ingest_files:
            with open(json_file, 'r', encoding='utf-8') as f:
                doc_data = json.load(f)
                ingested_docs.append(doc_data)

        # Fase 2: Summarization
        chunker_cfg = ChunkerConfig(
            max_tokens=1024,
            handle_audio_video=True,
            model_map="gpt-4o",
            model_reduce="gpt-4o",
            max_concurrency=5
        )
        chunker = Chunker(chunker_cfg)
        summarized_docs = asyncio.run(chunker.process_documents(ingested_docs))

        # Salva i risultati del summarization
        summary_files = []
        for i, doc in enumerate(summarized_docs):
            output_file = summary_output_dir / f"summary_{i}.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(doc, f, indent=2, ensure_ascii=False)
            summary_files.append(str(output_file))

        # Fase 3: Accumulation
        if summarized_docs:
            print("\n\n\n\nmarcello\n\n\n")
            print(summarized_docs)
            print("\n\n\nmarcello\n\n\n")
            accumulated_result = accumulation(summarized_docs)  # Prende il primo documento

            return {
                "status": "success",
                "files_processed": len(input_files),
                "summaries_created": len(summarized_docs),
                "accumulated_result": accumulated_result
            }

        return {"status": "success", "files_processed": len(input_files)}

    except Exception as e:
        return {"error": f"Errore durante l'elaborazione: {str(e)}"}

@app.route('/api/storico', methods=['GET'])
def get_storico():
    """Endpoint per recuperare lo storico dei documenti elaborati"""
    try:
        # Cerca tutti i file di summary nella directory output
        summary_dir = OUTPUT_FOLDER / "summary"
        summary_files = list(summary_dir.glob("*.json"))

        documents = []
        for file_path in summary_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    doc_data = json.load(f)
                    documents.append({
                        "id": file_path.stem,
                        "filename": file_path.name,
                        "data": doc_data,
                        "created_at": file_path.stat().st_mtime
                    })
            except Exception as e:
                print(f"Errore nel caricare {file_path}: {e}")
                continue

        # Ordina per data di creazione (più recenti primi)
        documents.sort(key=lambda x: x['created_at'], reverse=True)

        return jsonify({
            "status": "success",
            "documents": documents,
            "total": len(documents)
        })

    except Exception as e:
        return jsonify({"error": f"Errore nel recuperare lo storico: {str(e)}"}), 500

@app.route('/api/documents/<document_id>', methods=['GET'])
def get_document(document_id):
    """Endpoint per recuperare un documento specifico"""
    try:
        summary_dir = OUTPUT_FOLDER / "summary"
        file_path = summary_dir / f"{document_id}.json"

        if not file_path.exists():
            return jsonify({"error": "Documento non trovato"}), 404

        with open(file_path, 'r', encoding='utf-8') as f:
            doc_data = json.load(f)

        return jsonify({
            "status": "success",
            "document": doc_data
        })

    except Exception as e:
        return jsonify({"error": f"Errore nel recuperare il documento: {str(e)}"}), 500

@app.route('/api/documents/<document_id>', methods=['DELETE'])
def delete_document(document_id):
    """Endpoint per eliminare un documento"""
    try:
        summary_dir = OUTPUT_FOLDER / "summary"
        file_path = summary_dir / f"{document_id}.json"

        if not file_path.exists():
            return jsonify({"error": "Documento non trovato"}), 404

        file_path.unlink()

        return jsonify({
            "status": "success",
            "message": "Documento eliminato con successo"
        })

    except Exception as e:
        return jsonify({"error": f"Errore nell'eliminare il documento: {str(e)}"}), 500

@app.route('/api/clear', methods=['POST'])
def clear_all():
    """Endpoint per pulire tutti i file di input e output"""
    try:
        # Pulisci directory input
        for file_path in UPLOAD_FOLDER.iterdir():
            if file_path.is_file():
                file_path.unlink()

        # Pulisci directory output
        for subdir in OUTPUT_FOLDER.iterdir():
            if subdir.is_dir():
                for file_path in subdir.iterdir():
                    if file_path.is_file():
                        file_path.unlink()

        return jsonify({
            "status": "success",
            "message": "Tutti i file sono stati eliminati"
        })

    except Exception as e:
        return jsonify({"error": f"Errore nella pulizia: {str(e)}"}), 500

@app.errorhandler(413)
def too_large(e):
    return jsonify({"error": "File troppo grande. Dimensione massima: 100MB"}), 413

@app.errorhandler(500)
def internal_error(e):
    return jsonify({"error": "Errore interno del server"}), 500

if __name__ == '__main__':
    # Controlla che la variabile d'ambiente OPENAI_API_KEY sia impostata
    if not os.getenv("OPENAI_API_KEY"):
        print("ATTENZIONE: OPENAI_API_KEY non trovata nelle variabili d'ambiente!")
        print("Assicurati di impostare la chiave API di OpenAI prima di avviare il server.")

    print("Avvio del server Flask...")
    print("Server disponibile su: http://localhost:8000")
    print("Endpoint disponibili:")
    print("  - GET  /api/health - Health check")
    print("  - POST /api/upload - Upload e elaborazione file")
    print("  - GET  /api/storico - Recupera storico documenti")
    print("  - GET  /api/documents/<id> - Recupera documento specifico")
    print("  - DELETE /api/documents/<id> - Elimina documento")
    print("  - POST /api/clear - Pulisci tutti i file")

    app.run(debug=True, host='0.0.0.0', port=8000)
