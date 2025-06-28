import { useState } from "react";
import FileUploader from "./components/FileUploader.jsx";
import Sidebar from "./components/SideBar.jsx";
import SummaryViewer from "./components/SummaryViewer";

export default function App() {
  const [selectedSummary, setSelectedSummary] = useState(null);

  return (
    <div style={{ display: "flex" }}>
      <Sidebar onSelect={setSelectedSummary} />
      <div style={{ flex: 1 }}>
        <FileUploader onUploaded={setSelectedSummary} />
        <SummaryViewer summary={selectedSummary} />
      </div>
    </div>
  );
}
