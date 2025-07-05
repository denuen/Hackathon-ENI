import { useState, useRef } from "react";

export default function FileUploader({ onUploaded }) {
  const [files, setFiles] = useState([]);
  const [keyword, setKeyword] = useState("");
  const [keywords, setKeywords] = useState([]);
  const [keywordError, setKeywordError] = useState("");
  const [loading, setLoading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [currentTask, setCurrentTask] = useState("");
  const inputRef = useRef(null);

  const handleFileChange = (e) => {
    const newFiles = Array.from(e.target.files);
    setFiles((currFiles) => {
      const existingNames = new Set(currFiles.map(f => f.name));
      const filteredNewFiles = newFiles.filter(f => !existingNames.has(f.name));
      return [...currFiles, ...filteredNewFiles];
    });
  };

  const triggerFileSelect = () => {
    inputRef.current.click();
  };

  const removeFile = (index) => {
    setFiles((currFiles) => currFiles.filter((_, i) => i !== index));
  };

  const addKeyword = () => {
    const trimmed = keyword.trim();
    if (trimmed && !keywords.includes(trimmed)) {
      setKeywords((prev) => [...prev, trimmed]);
      setKeywordError("");
    }
    setKeyword("");
  };

  const removeKeyword = (index) => {
    setKeywords((prev) => prev.filter((_, i) => i !== index));
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter") {
      e.preventDefault();
      addKeyword();
    }
  };

  const handleUpload = async () => {
    if (files.length === 0) {
      alert("Seleziona almeno un file");
      return;
    }

    setLoading(true);
    setProgress(0);
    setCurrentTask("Inizializzazione...");

    const stopProgress = simulateProgress();

    try {
      const formData = new FormData();
      files.forEach(file => formData.append("files", file));
      keywords.forEach(kw => formData.append("keywords", kw));

      console.log("Inizio upload con timeout di 10 minuti...");
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 600000); // 10 minuti

      const res = await fetch("/api/upload", {
        method: "POST",
        body: formData,
        signal: controller.signal
      });

      clearTimeout(timeoutId);
      stopProgress();

      if (!res.ok) {
        const errorData = await res.json().catch(() => ({ error: "Errore sconosciuto" }));
        throw new Error(errorData.error || `Errore HTTP ${res.status}`);
      }

      const data = await res.json();
      console.log("Upload completato con successo:", data);

      setProgress(100);
      setCurrentTask("Completato!");

      onUploaded(data);
      setKeywordError("");
    } catch (err) {
      console.error("Errore durante l'upload:", err);
      stopProgress();
      setProgress(0);
      setCurrentTask("");

      if (err.name === 'AbortError') {
        alert("Timeout: L'elaborazione sta richiedendo troppo tempo. Riprova con file più piccoli.");
      } else {
        alert(`Errore durante l'upload: ${err.message}`);
      }
    } finally {
      setLoading(false);
      setTimeout(() => {
        setProgress(0);
        setCurrentTask("");
      }, 2000);
    }
  };

  // Funzione per simulare il progresso dell'elaborazione
  const simulateProgress = () => {
    const progressSteps = [
      { progress: 5, message: "Caricamento file...", delay: 500 },
      { progress: 15, message: "Analisi dei documenti...", delay: 1200 },
      { progress: 25, message: "Estrazione del contenuto...", delay: 1800 },
      { progress: 35, message: "Elaborazione con AI...", delay: 2500 },
      { progress: 50, message: "Generazione riassunti...", delay: 3000 },
      { progress: 65, message: "Applicazione focus keywords...", delay: 2200 },
      { progress: 75, message: "Organizzazione delle sezioni...", delay: 1500 },
      { progress: 85, message: "Strutturazione finale...", delay: 1800 },
      { progress: 95, message: "Completamento...", delay: 1000 }
    ];

    let currentStep = 0;

    const runNextStep = () => {
      if (currentStep < progressSteps.length) {
        const step = progressSteps[currentStep];
        setProgress(step.progress);
        setCurrentTask(step.message);
        currentStep++;

        setTimeout(runNextStep, step.delay + Math.random() * 500);
      }
    };

    // Avvia la simulazione
    runNextStep();

    // funzione per fermare la simulazione
    return () => {
      currentStep = progressSteps.length;
    };
  };

  return (
    <div className="file-uploader">
      <input
        type="file"
        multiple
        ref={inputRef}
        onChange={handleFileChange}
        style={{ display: "none" }}
        disabled={loading}
      />

      <div className="button-group">
        <button
          type="button"
          onClick={triggerFileSelect}
          className="select-file-btn"
          disabled={loading}
        >
          Scegli file
        </button>
        <button
          onClick={handleUpload}
          className="upload-btn"
          disabled={loading}
        >
          {loading ? "Elaborazione in corso..." : "Riassumi"}
        </button>
        {loading && (
          <div className="spinner" aria-label="Caricamento in corso"></div>
        )}
      </div>

      {/* Barra di progresso */}
      {loading && (
        <div className="progress-container">
          <div className="progress-bar">
            <div
              className="progress-fill"
              style={{ width: `${progress}%` }}
            ></div>
          </div>
          <div className="progress-text">
            <span className="progress-percentage">{progress}%</span>
            <span className="progress-message">{currentTask}</span>
          </div>
        </div>
      )}

      <div className="keywords-section">
        <div style={{ display: "flex", gap: "8px", alignItems: "center" }}>
          <input
            id="keyword-input"
            type="text"
            placeholder="Inserisci keyword"
            value={keyword}
            onChange={(e) => setKeyword(e.target.value)}
            onKeyDown={handleKeyDown}
            className={`keyword-input ${keywordError ? "keyword-input-error" : ""}`}
            aria-describedby="keyword-error keyword-instruction"
            disabled={loading}
            style={{ flexGrow: 1 }}
          />
          <button
            type="button"
            onClick={addKeyword}
            disabled={loading}
            aria-label="Aggiungi keyword"
            className="add-keyword-btn"
          >
            Invio
          </button>
        </div>
        <small
          id="keyword-instruction"
          style={{ display: "block", marginTop: 4, color: "#666", fontSize: "0.85rem" }}
        >
          Premi o clicca "Invio" per aggiungere la keyword
        </small>
        {keywordError && (
          <p id="keyword-error" className="keyword-error-message">
            {keywordError}
          </p>
        )}
        <div className="keyword-list">
          {keywords.map((kw, i) => (
            <span key={i} className="keyword-tag">
              {kw}
              <button
                type="button"
                className="remove-keyword-btn"
                onClick={() => removeKeyword(i)}
                aria-label={`Rimuovi keyword ${kw}`}
                disabled={loading}
              >
                ✕
              </button>
            </span>
          ))}
        </div>
      </div>

      <div className="file-list">
        {files.length > 0 ? (
          files.map((file, i) => (
            <div key={i} className="file-item">
              {file.name}
              <button
                type="button"
                className="remove-file-btn"
                onClick={() => removeFile(i)}
                aria-label={`Rimuovi file ${file.name}`}
                disabled={loading}
              >
                ✕
              </button>
            </div>
          ))
        ) : (
          <small></small>
        )}
      </div>
    </div>
  );
}
