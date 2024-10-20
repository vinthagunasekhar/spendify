// src/App.js
import React, { useState } from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';

import CardForm from './components/cardForm';
import AddCardConfirmation from './pages/AddCardConfirmation';
import StrategyPage from './pages/StrategyPage';
import { Container } from '@mui/material';

const App = () => {
  const [cardAdded, setCardAdded] = useState(false);

  const handleCardAdded = () => {
    setCardAdded(true);
  };

  const handleBackToForm = () => {
    setCardAdded(false);
  };

  return (
    <Router>
      <Container>
        <Routes>
          <Route path="/" element={cardAdded ? <AddCardConfirmation onBack={handleBackToForm} /> : <CardForm onCardAdded={handleCardAdded} />} />
          <Route path="/strategy" element={<StrategyPage />} />
        </Routes>
      </Container>
    </Router>
  );
};

export default App;