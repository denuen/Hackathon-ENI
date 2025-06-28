import { useState } from "react";

export default function FileUploader({ onUploaded }) {
  const [files, setFiles] = useState([]);

  const handleUpload = async () => {
    const formData = new FormData();
    files.forEach(file => formData.append("files", file));

    const res = await fetch("http://localhost:5000/api/upload", {
      method: "POST",
      body: formData
    });

    const data = await res.json();
    onUploaded(data);  // aggiorna con nuova sintesi
  };

  return (
    <div>
      <input type="file" multiple onChange={e => setFiles([...e.target.files])} />
      <button onClick={handleUpload}>Carica</button>
    </div>
  );
}
