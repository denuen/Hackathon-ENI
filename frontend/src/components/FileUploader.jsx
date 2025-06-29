import { useState, useRef } from "react";

export default function FileUploader({ onUploaded }) {
  const [files, setFiles] = useState([]);
  const [keyword, setKeyword] = useState("");
  const [keywords, setKeywords] = useState([]);
  const [keywordError, setKeywordError] = useState("");
  const [loading, setLoading] = useState(false);
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

    if (keywords.length === 0) {
      setKeywordError("Inserisci almeno una keyword prima di procedere");
      return;
    }

    setLoading(true);
    try {
      const formData = new FormData();
      files.forEach(file => formData.append("files", file));
      keywords.forEach(kw => formData.append("keywords", kw));

      const res = await fetch("/api/upload", {
        method: "POST",
        body: formData
      });

      const data = await res.json();
      onUploaded(data);
      setKeywordError("");
    } catch (err) {
      alert("Errore durante l'upload");
    } finally {
      setLoading(false);
    }
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
          {loading ? "Caricamento..." : "Riassumi"}
        </button>
        {loading && (
          <div className="spinner" aria-label="Caricamento in corso"></div>
        )}
      </div>

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
