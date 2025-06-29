import { useEffect, useState } from "react";
import SummyLogo from "../../assets/SummyDef.png";

export default function SideBar({ onSelect }) {
  const [storico, setStorico] = useState([]);
  const [loading, setLoading] = useState(true);
  const [errore, setErrore] = useState(false);

  useEffect(() => {
    fetch("/api/storico")
      .then(res => {
        if (!res.ok) throw new Error();
        return res.json();
      })
      .then(data => {
        if (Array.isArray(data)) setStorico(data);
        else setErrore(true);
      })
      .catch(() => setErrore(true))
      .finally(() => setLoading(false));
  }, []);

  return (
    <aside className="sidebar">
      <img
        src={SummyLogo}
        alt="Logo Summy"
        className="sidebar-logo"
      />
      <h3 className="sidebar-title">Storico</h3>

      {loading && <p>Caricamento...</p>}
      {!loading && errore && <p className="sidebar-placeholder-empty">Nessun riassunto disponibile</p>}
      {!loading && !errore && storico.length === 0 && (
        <p className="sidebar-placeholder-empty">Nessun riassunto disponibile</p>
      )}

      <ul>
        {storico.map((item, idx) => (
          <li key={idx} onClick={() => onSelect(item)}>
            {item.Titolo ?? `Elemento ${idx + 1}`}
          </li>
        ))}
      </ul>
    </aside>
  );
}
