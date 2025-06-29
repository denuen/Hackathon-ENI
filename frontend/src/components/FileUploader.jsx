import { useState, useRef } from "react";

export default function FileUploader({ onUploaded }) {
  const [files, setFiles] = useState([]);
  const [keyword, setKeyword] = useState("");
  const [keywords, setKeywords] = useState([]);
  const [keywordError, setKeywordError] = useState(""); // stato per errore keyword
  const inputRef = useRef(null);

  const handleFileChange = (e) => {
    setFiles([...e.target.files]);
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
      setKeywordError(""); // reset errore se aggiunta keyword valida
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
      setKeywordError(""); // reset errore in caso di successo
    } catch (err) {
      alert("Errore durante l'upload");
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
      />

      <div className="button-group">
        <button type="button" onClick={triggerFileSelect} className="select-file-btn">
          Scegli file
        </button>
        <button onClick={handleUpload} className="upload-btn">
          Riassumi
        </button>
      </div>

      <div className="keywords-section">
        <input
          type="text"
          placeholder="Aggiungi una keyword e premi Invio"
          value={keyword}
          onChange={(e) => setKeyword(e.target.value)}
          onKeyDown={handleKeyDown}
          className={`keyword-input ${keywordError ? "keyword-input-error" : ""}`}
          aria-describedby="keyword-error"
        />
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
