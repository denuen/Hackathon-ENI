import { useEffect, useState } from "react";

export default function Sidebar({ onSelect }) {
  const [storico, setStorico] = useState([]);

  useEffect(() => {
    fetch("http://localhost:5000/api/storico")
      .then(res => res.json())
      .then(data => setStorico(data));
  }, []);

  return (
    <aside>
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
