import React from "react";
import {
  BrowserRouter as Router,
  Routes,
  Route,
  Navigate,
} from "react-router-dom";
import Upload from "./Pages/Upload";
import SeeResult from "./Pages/SeeResult";

function App() {
  return (
    <Router>
      <div className="App">
        <Routes>
          <Route path="/" element={<Navigate to="/upload" replace />} />
          <Route path="/upload" element={<Upload />} />
          <Route path="/results" element={<SeeResult />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
