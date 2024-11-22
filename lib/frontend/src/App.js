import React from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import { Container, CssBaseline } from '@mui/material'; // Import MUI components
import Navbar from './components/Navbar';
import HomePage from './pages/HomePage';
import ProcessPage from './pages/ProcessPage';
import PipelinePage from './pages/PipelinePage';
import PipelineView from './pages/PipelineView';

const App = () => {
  return (
    <Router>
      <CssBaseline /> {/* Normalize styles */}
      <Navbar />
      <Container maxWidth="lg"> {/* Set container max width */}
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/processes" element={<ProcessPage />} />
          <Route path="/pipelines" element={<PipelinePage />} />
          <Route path="/pipeline-view" element={<PipelineView />} />
        </Routes>
      </Container>
    </Router>
  );
};

export default App;
