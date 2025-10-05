import React from "react";
import { Routes, Route } from "react-router-dom";
import Dashboard from "./pages/Dashboard";
import Laboratory from "./pages/Laboratory";
import Search from "./pages/Search";
import Publication from "./pages/Publication";
import Training from "./pages/Training";
import DatasetDetail from "./pages/DatasetDetail";
import NotFound from "./pages/NotFound";

const App: React.FC = () => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-space to-spacestation">
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/laboratory" element={<Laboratory />} />
        <Route path="/search" element={<Search />} />
        <Route path="/publication" element={<Publication />} />
        <Route path="/training" element={<Training />} />
        <Route path="/dataset/:id" element={<DatasetDetail />} />
        <Route path="*" element={<NotFound />} />
      </Routes>
    </div>
  );
};

export default App;
