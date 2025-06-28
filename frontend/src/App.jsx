import { useState } from "react";
import FileUploader from "./components/FileUploader.jsx";
import SideBar from "./components/SideBar.jsx";
import SummaryViewer from "./components/SummaryViewer.jsx";
import "./App.css";

export default function App() {
  const [selectedSummary, setSelectedSummary] = useState(null);

  return (
    <div className="app-container">
      <div className="sidebar">
        <SideBar onSelect={setSelectedSummary} />
      </div>
      <div className="main-content">
        <div className="file-uploader">
          <FileUploader onUploaded={setSelectedSummary} />
        </div>
        <div className="summary-viewer">
          <SummaryViewer summary={selectedSummary} />
        </div>
      </div>
    </div>
  );
}
