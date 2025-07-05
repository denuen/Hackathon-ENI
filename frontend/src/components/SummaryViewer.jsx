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
	const keywordsUsed = summary.processing_result.keywords_used || [];

	return (
	  <div className="chat-output">
	    <h2>📄 Risultato Elaborato</h2>

	    {/* Sezione Keywords utilizzate */}
	    {keywordsUsed.length > 0 && (
	      <div className="keywords-used-section">
	        <h3 className="keywords-used-title">
	          Focus utilizzato per l'elaborazione:
	        </h3>
	        <div className="keywords-used-list">
	          {keywordsUsed.map((keyword, index) => (
	            <span key={index} className="keyword-used-tag">
	              {keyword}
	            </span>
	          ))}
	        </div>
	      </div>
	    )}

	    {/* Titolo principale */}
	    {titolo && <h3 className="summary-title">{titolo}</h3>}

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
