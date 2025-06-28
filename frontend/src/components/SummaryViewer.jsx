export default function SummaryViewer({ summary }) {
	if (!summary) return <p>Seleziona un riassunto dalla barra laterale</p>;
      
	return (
	  <div>
	    <h2>Risultato</h2>
	    <pre>{JSON.stringify(summary, null, 2)}</pre>
	  </div>
	);
      }
      