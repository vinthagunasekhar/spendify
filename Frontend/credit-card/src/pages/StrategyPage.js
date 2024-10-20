// src/StrategyPage.js
import React from 'react';
import { Container, Typography, Button } from '@mui/material';

const StrategyPage = () => {
  return (
    <Container maxWidth="md" style={{ marginTop: '20px' }}>
      <Typography variant="h4" gutterBottom>
        Strategy Page
      </Typography>
      <Typography variant="body1" gutterBottom>
        This page will contain strategy-related functionalities and details.
      </Typography>
      <Button variant="contained" color="primary">
        Learn More
      </Button>
    </Container>
  );
};

export default StrategyPage;
