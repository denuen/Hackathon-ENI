// frontend/src/components/SummaryViewer.jsx

export default function SummaryViewer({ summary }) {
	if (!summary) {
	  return (
	    <div className="chat-placeholder">
	      <p>Nessun contenuto disponibile. Carica un file per iniziare.</p>
	    </div>
	  );
	}
      
	return (
	  <div className="chat-output">
	    <h2>📄 Risultato Elaborato</h2>
	    <ul className="chat-summary-list">
	      {Array.isArray(summary)
		? summary.map((item, index) => (
		    <li key={index} className="chat-summary-item">
		      <h4>{item.title}</h4>
		      <p>{item.content}</p>
		    </li>
		  ))
		: <pre>{JSON.stringify(summary, null, 2)}</pre>}
	    </ul>
	  </div>
	);
      }
      