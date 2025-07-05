# Summy - Sistema di Elaborazione e Sintesi Documenti

Un sistema completo per l'elaborazione, summarization e visualizzazione di documenti aziendali con supporto per parole chiave tematiche.

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
// Upload file con keywords
const formData = new FormData();
formData.append("files", file);
formData.append("keywords", JSON.stringify(["energia", "sostenibilità", "ambiente"]));

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
│ • Keywords      │    │ • Keywords API  │    │ • Thematic Focus│
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 📂 Struttura Progetto

```
├── app.py                 # API Flask principale
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

- Upload multipli file con supporto per oltre 30 formati
- Supporto per parole chiave tematiche che influenzano l'elaborazione
- Estrazione automatica contenuti da documenti, audio e video
- Summarization intelligente con GPT-4 orientata alle keywords
- Accumulazione e formattazione risultati con focus tematico

### Gestione Keywords

- Inserimento parole chiave per guidare l'elaborazione
- Filtro tematico automatico durante la summarization
- Creazione di documenti finali focalizzati sui temi di interesse
- Visualizzazione keywords utilizzate nel risultato finale

### Gestione Documenti

- Storico documenti elaborati
- Visualizzazione risultati
- Eliminazione documenti
- Pulizia sistema

### Tipi di File Supportati

- **Documenti**: PDF, TXT, DOC, DOCX, ODT, RTF, PPT, PPTX, ODP, XLSX, XLS, ODS, CSV, XML, JSON
- **Immagini**: JPG, JPEG, PNG, BMP, TIFF, TIF, GIF, WEBP, SVG
- **Audio**: MP3, WAV, M4A, AAC, FLAC, OGG, WMA, AMR, OPUS
- **Video**: MOV, MP4, AVI, MKV, WMV, WEBM, M4V, FLV, 3GP, MPG, MPEG

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

- Lingue supportate per OCR e elaborazione documenti
- Modelli Whisper per trascrizione audio e video
- Configurazioni OpenAI per la summarization
- Prompt personalizzati per chunking e accumulation
- Terminologia e contesto specifici per il dominio aziendale

## 🛠️ Sviluppo

### Test API

```bash
# Health check
curl http://localhost:8000/api/health

# Upload file con keywords
curl -X POST \
  -F "files=@document.pdf" \
  -F "keywords=[\"energia\", \"sostenibilità\"]" \
  http://localhost:8000/api/upload

# Recupera storico
curl http://localhost:8000/api/storico
```

### Debug

- Backend: I log sono visibili nella console Flask
- Frontend: Utilizza DevTools del browser
- Errori API: Controllare la risposta JSON per dettagli

## 📝 Note Importanti

1. **Chiave API**: Assicurati che `OPENAI_API_KEY` sia impostata
2. **Dimensioni File**: Limite massimo 100MB per file
3. **Keywords**: Le parole chiave influenzano direttamente l'elaborazione e la sintesi
4. **Concorrenza**: Configurabile nel `ChunkerConfig`
5. **Storage**: I file vengono salvati localmente nelle directory `input/` e `output/`

## 🔑 Sistema Keywords

### Funzionamento Tecnico

Le keywords vengono integrate nel processo di elaborazione a più livelli:

1. **Chunking Phase**: Le keywords guidano la suddivisione del contenuto, privilegiando sezioni tematicamente correlate
2. **Summarization Phase**: Ogni chunk viene sintetizzato con focus specifico sui temi delle keywords
3. **Accumulation Phase**: I risultati vengono organizzati e strutturati mantenendo la coerenza tematica

### Utilizzo nell'API

```json
{
  "keywords": ["energia rinnovabile", "sostenibilità", "ambiente"],
  "files": ["documento.pdf", "presentazione.pptx"]
}
```

### Impatto sull'Output

- **Senza keywords**: Sintesi generale del contenuto
- **Con keywords**: Documento finale focalizzato sui temi specificati
- **Filtraggio automatico**: Le informazioni non correlate vengono minimizzate
- **Strutturazione tematica**: L'output segue la logica delle keywords fornite

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

## 👥 Sviluppatori

Summy è stato sviluppato da:

- **Antonio Pintauro**
- **Marcello Pisani**
- **Ahmed Abdelrahman**

⏱️ **Tempo di sviluppo**: 15 ore di pura magia (e tanti, forse troppi caffè)

