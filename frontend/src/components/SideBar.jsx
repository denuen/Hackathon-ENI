import { useEffect, useState } from "react";
import SummyLogo from "../../assets/SummyDef.png"; // assicurati che il path sia corretto

export default function SideBar({ onSelect }) {
  const [storico, setStorico] = useState([]);

  useEffect(() => {
    fetch("http://localhost:5000/api/storico")
      .then(res => res.json())
      .then(data => setStorico(data));
  }, []);

  return (
    <aside className="sidebar">
      <img
        src={SummyLogo}
        alt="Logo Summy"
        className="sidebar-logo"
      />
      <h3>Storico</h3>
      <ul>
        {storico.map((item, idx) => (
          <li key={idx} onClick={() => onSelect(item)}>
            {item.timestamp.slice(0, 16)}...
          </li>
        ))}
      </ul>
    </aside>
  );
}
