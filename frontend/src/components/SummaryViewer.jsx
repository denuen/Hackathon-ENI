export default function SummaryViewer({ summary }) {
	if (
	  !summary ||
	  !summary.processing_result ||
	  !summary.processing_result.accumulated_result
	) {
	  return (
	    <div className="chat-placeholder">
	      <p>Nessun contenuto disponibile. Riassumi un file per visualizzare il risultato.</p>
	    </div>
	  );
	}
      
	const result = summary.processing_result.accumulated_result;
	const titolo = result.Titolo;
	const sezioni = result.Sezioni;
      
	return (
	  <div className="chat-output">
	    <h2>📄 Risultato Elaborato</h2>
      
	    {/* Titolo principale */}
	    {titolo && <h3 style={{ fontWeight: "bold" }}>{titolo}</h3>}
      
	    <ul className="chat-summary-list">
	      {Array.isArray(sezioni)
		? sezioni.map((item, index) => (
		    <li key={index} className="chat-summary-item">
		      <h4>{item.titolo}</h4>
		      <p>{item.contenuto}</p>
		    </li>
		  ))
		: <p>Nessuna sezione trovata.</p>}
	    </ul>
	  </div>
	);
      }