# Hackathon ENI - Sistema di Elaborazione Documenti

Un sistema completo per l'elaborazione, summarization e visualizzazione di documenti aziendali ENI.

## 🚀 Avvio Rapido

### Prerequisiti

- Python 3.8+
- Node.js 16+
- npm o yarn
- Chiave API OpenAI

### 1. Configurazione Backend

```bash
# Clona il repository e naviga nella directory
cd Hackathon-ENI

# Crea e attiva virtual environment
python3 -m venv venv
source venv/bin/activate  # Su macOS/Linux
# oppure
venv\Scripts\activate     # Su Windows

# Installa dipendenze
pip install -r requirements.txt

# Imposta la chiave API di OpenAI
export OPENAI_API_KEY='your-openai-api-key-here'
```

### 2. Avvio Backend (Flask API)

```bash
# Avvia il server Flask
python app.py
```

Il server sarà disponibile su `http://localhost:8000`

### 3. Configurazione Frontend

```bash
# In un nuovo terminale, naviga nella directory frontend
cd frontend

# Installa dipendenze Node.js
npm install

# Avvia il server di sviluppo
npm run dev
```

Il frontend sarà disponibile su `http://localhost:5173` (o porta simile)

### 4. Script di Avvio Automatico

Per semplificare l'avvio, puoi utilizzare lo script fornito:

```bash
# Rendi eseguibile lo script
chmod +x start.sh

# Esegui lo script
./start.sh
```

## 📚 API Endpoints

### Backend (Flask) - `http://localhost:8000/api`

| Endpoint          | Metodo | Descrizione                  |
| ----------------- | ------ | ---------------------------- |
| `/health`         | GET    | Health check del server      |
| `/upload`         | POST   | Upload e elaborazione file   |
| `/storico`        | GET    | Recupera storico documenti   |
| `/documents/<id>` | GET    | Recupera documento specifico |
| `/documents/<id>` | DELETE | Elimina documento            |
| `/clear`          | POST   | Pulisci tutti i file         |

### Esempio di utilizzo:

```javascript
// Upload file
const formData = new FormData();
formData.append("files", file);

fetch("http://localhost:8000/api/upload", {
  method: "POST",
  body: formData,
})
  .then((res) => res.json())
  .then((data) => console.log(data));
```

## 🔧 Architettura del Sistema

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Flask API     │    │   Processing    │
│   (React)       │◄──►│   (Backend)     │◄──►│   Pipeline      │
│                 │    │                 │    │                 │
├─────────────────┤    ├─────────────────┤    ├─────────────────┤
│ • FileUploader  │    │ • Upload files  │    │ • Ingest        │
│ • SummaryViewer │    │ • Process docs  │    │ • Summarization │
│ • SideBar       │    │ • Store results │    │ • Accumulation  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 📂 Struttura Progetto

```
├── app.py                 # API Flask principale
├── summy.py              # Script di elaborazione standalone
├── start.sh              # Script di avvio automatico
├── requirements.txt      # Dipendenze Python
├── config.json          # Configurazioni del sistema
│
├── frontend/             # Applicazione React
│   ├── src/
│   │   ├── components/   # Componenti React
│   │   └── api.js       # Client API
│   └── package.json
│
├── ingest/              # Moduli di ingest
│   └── extractor.py     # Estrazione contenuti
│
├── summarize/           # Moduli di summarization
│   └── chunker.py       # Chunking e summarization
│
├── formatting/          # Moduli di formattazione
│   ├── accumulation.py  # Accumulazione risultati
│   ├── flushing.py     # Output formatting
│   └── storing.py      # Storage documenti
│
├── input/              # File di input
├── output/             # File elaborati
│   ├── ingest/         # Output ingest
│   └── summary/        # Output summarization
└── utils/              # Utilities
```

## 🎯 Funzionalità

### Upload e Elaborazione

- Upload multipli file (PDF, DOC, CSV, audio, video)
- Estrazione automatica contenuti
- Summarization intelligente con GPT-4
- Accumulazione e formattazione risultati

### Gestione Documenti

- Storico documenti elaborati
- Visualizzazione risultati
- Eliminazione documenti
- Pulizia sistema

### Tipi di File Supportati

- **Documenti**: PDF, DOC, DOCX, TXT, CSV
- **Audio**: MP3, WAV
- **Video**: MP4, AVI, MOV

## ⚙️ Configurazione

### Variabili d'Ambiente

```bash
# Obbligatoria
export OPENAI_API_KEY='your-openai-api-key-here'

# Opzionali
export FLASK_ENV=development
export FLASK_DEBUG=True
```

### Configurazione in `config.json`

- Lingue supportate per OCR
- Modelli Whisper per trascrizione audio
- Terminologia corporativa specifica ENI
- Prompt iniziali multilingua

## 🛠️ Sviluppo

### Test API

```bash
# Health check
curl http://localhost:8000/api/health

# Upload file
curl -X POST -F "files=@document.pdf" http://localhost:8000/api/upload

# Recupera storico
curl http://localhost:8000/api/storico
```

### Debug

- Backend: I log sono visibili nella console Flask
- Frontend: Utilizza DevTools del browser
- Errori API: Controllare la risposta JSON per dettagli

## 📝 Note Importanti

1. **Chiave API**: Assicurati che `OPENAI_API_KEY` sia impostata
2. **Dimensioni File**: Limite massimo 16MB per file
3. **Concorrenza**: Configurabile nel `ChunkerConfig`
4. **Storage**: I file vengono salvati localmente nelle directory `input/` e `output/`

## 🤝 Contributi

Per contribuire al progetto:

1. Fork del repository
2. Crea un branch per la feature
3. Commit delle modifiche
4. Push al branch
5. Apri una Pull Request

## 📞 Supporto

Per problemi o domande:

- Controlla i log del server Flask
- Verifica la configurazione delle variabili d'ambiente
- Assicurati che tutte le dipendenze siano installate correttamente
