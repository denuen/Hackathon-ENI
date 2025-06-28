export async function uploadFiles(files) {
	const formData = new FormData();
	files.forEach(file => formData.append("files", file));
	const res = await fetch("http://localhost:5000/api/upload", {
	  method: "POST",
	  body: formData
	});
	return await res.json();
      }
      
      export async function getStorico() {
	const res = await fetch("http://localhost:5000/api/storico");
	return await res.json();
      }
      