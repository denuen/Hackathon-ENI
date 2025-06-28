import { useState, useRef } from "react";

export default function FileUploader({ onUploaded }) {
  const [files, setFiles] = useState([]);
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

  const handleUpload = async () => {
    if (files.length === 0) return alert("Seleziona almeno un file");

    const formData = new FormData();
    files.forEach(file => formData.append("files", file));

    const res = await fetch("http://localhost:5000/api/upload", {
      method: "POST",
      body: formData
    });

    const data = await res.json();
    onUploaded(data);
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
      <button type="button" onClick={triggerFileSelect} className="select-file-btn">
        Scegli file
      </button>
      <button onClick={handleUpload} className="upload-btn">
        Carica
      </button>
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
          <small>Seleziona un file</small>
        )}
      </div>
    </div>
  );
}
