// src/AddCardConfirmation.js
import React from 'react';
import { Container, Typography, Button } from '@mui/material';

const AddCardConfirmation = ({ onBack }) => {
  return (
    <Container maxWidth="sm" style={{ marginTop: '20px', textAlign: 'center' }}>
      <Typography variant="h4" gutterBottom>
        Card Added Successfully!
      </Typography>
      <Typography variant="body1" gutterBottom>
        Your card has been added to the system.
      </Typography>
      <Button variant="contained" color="primary" onClick={onBack}>
        Back to Add Another Card
      </Button>
    </Container>
  );
};

export default AddCardConfirmation;
