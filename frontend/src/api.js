const API_BASE_URL = "/api";

export async function uploadFiles(files) {
  try {
    const formData = new FormData();
    files.forEach(file => formData.append("files", file));

    const res = await fetch(`${API_BASE_URL}/upload`, {
      method: "POST",
      body: formData
    });

    if (!res.ok) {
      throw new Error(`HTTP error! status: ${res.status}`);
    }

    return await res.json();
  } catch (error) {
    console.error("Errore durante l'upload:", error);
    throw error;
  }
}

export async function getStorico() {
  try {
    const res = await fetch(`${API_BASE_URL}/storico`);

    if (!res.ok) {
      throw new Error(`HTTP error! status: ${res.status}`);
    }

    return await res.json();
  } catch (error) {
    console.error("Errore nel recuperare lo storico:", error);
    throw error;
  }
}

export async function getDocument(documentId) {
  try {
    const res = await fetch(`${API_BASE_URL}/documents/${documentId}`);

    if (!res.ok) {
      throw new Error(`HTTP error! status: ${res.status}`);
    }

    return await res.json();
  } catch (error) {
    console.error("Errore nel recuperare il documento:", error);
    throw error;
  }
}

export async function deleteDocument(documentId) {
  try {
    const res = await fetch(`${API_BASE_URL}/documents/${documentId}`, {
      method: "DELETE"
    });

    if (!res.ok) {
      throw new Error(`HTTP error! status: ${res.status}`);
    }

    return await res.json();
  } catch (error) {
    console.error("Errore nell'eliminare il documento:", error);
    throw error;
  }
}

export async function clearAll() {
  try {
    const res = await fetch(`${API_BASE_URL}/clear`, {
      method: "POST"
    });

    if (!res.ok) {
      throw new Error(`HTTP error! status: ${res.status}`);
    }

    return await res.json();
  } catch (error) {
    console.error("Errore nella pulizia:", error);
    throw error;
  }
}

export async function healthCheck() {
  try {
    const res = await fetch(`${API_BASE_URL}/health`);

    if (!res.ok) {
      throw new Error(`HTTP error! status: ${res.status}`);
    }

    return await res.json();
  } catch (error) {
    console.error("Errore nel health check:", error);
    throw error;
  }
}
