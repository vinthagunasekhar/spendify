import React, { useState, useEffect } from 'react';
import axios from 'axios';
import {
  Container,
  TextField,
  Select,
  MenuItem,
  Button,
  Typography,
  FormControl,
  InputLabel,
  Snackbar,
  Alert,
} from '@mui/material';

const CardForm = () => {
  const [cardData, setCardData] = useState({
    name: '',
    billing_start: '',
    billing_end: '',
    limit_option: 'A',
    limit_value: '',
  });
  const [availableCards, setAvailableCards] = useState([]);
  const [successMessage, setSuccessMessage] = useState('');
  const [errorMessage, setErrorMessage] = useState('');

  // Fetch available card names when the component mounts
  useEffect(() => {
    axios.get('http://localhost:5000/available-cards')
      .then((response) => {
        setAvailableCards(response.data);
      })
      .catch((error) => {
        console.error('Error fetching card names:', error);
      });
  }, []);

  const handleChange = (event) => {
    const { name, value } = event.target;
    setCardData((prevData) => ({ ...prevData, [name]: value }));
  };

  const handleSubmit = (event) => {
    event.preventDefault();

    // Parse values before sending to the backend
    const parsedData = {
      name: cardData.name,
      billing_start: parseInt(cardData.billing_start, 10), // Convert to integer
      billing_end: parseInt(cardData.billing_end, 10),     // Convert to integer
      limit_option: cardData.limit_option,
      limit_value: parseFloat(cardData.limit_value),         // Convert to float
    };

    console.log('Data being sent to the backend:', parsedData);
    axios.post('http://localhost:5000/add-card', parsedData)
      .then((response) => {
        setSuccessMessage('Card added successfully!');
        setErrorMessage('');
        setCardData({ name: '', billing_start: '', billing_end: '', limit_option: 'A', limit_value: '' });
      })
      .catch((error) => {
        setErrorMessage('Failed to add the card. Please check your input.');
        setSuccessMessage('');
      });
  };

  return (
    <Container maxWidth="sm" style={{ marginTop: '20px' }}>
      <Typography variant="h4" align="center" gutterBottom>
        Add a New Card
      </Typography>
      <form onSubmit={handleSubmit}>
        <FormControl fullWidth margin="normal">
          <InputLabel>Card Name</InputLabel>
          <Select
            name="name"
            value={cardData.name}
            onChange={handleChange}
            required
          >
            <MenuItem value=""><em>Select a card</em></MenuItem>
            {availableCards.map((card) => (
              <MenuItem key={card} value={card}>{card}</MenuItem>
            ))}
          </Select>
        </FormControl>
        <TextField
          type="number"
          name="billing_start"
          label="Billing Start Date"
          value={cardData.billing_start}
          onChange={handleChange}
          InputProps={{ inputProps: { min: 1, max: 31 } }}
          fullWidth
          required
        />
        <TextField
          type="number"
          name="billing_end"
          label="Billing End Date"
          value={cardData.billing_end}
          onChange={handleChange}
          InputProps={{ inputProps: { min: 1, max: 31 } }}
          fullWidth
          required
        />
        <FormControl fullWidth margin="normal">
          <InputLabel>Limit Option</InputLabel>
          <Select
            name="limit_option"
            value={cardData.limit_option}
            onChange={handleChange}
          >
            <MenuItem value="A">Specific Limit</MenuItem>
            <MenuItem value="B">No Limit</MenuItem>
          </Select>
        </FormControl>
        {cardData.limit_option === 'A' && (
          <TextField
            type="number"
            name="limit_value"
            label="Limit Value"
            value={cardData.limit_value}
            onChange={handleChange}
            InputProps={{ inputProps: { min: 0 } }}
            fullWidth
            required // Added required if needed
          />
        )}
        <Button variant="contained" color="primary" type="submit" fullWidth>
          Add Card
        </Button>
      </form>
      <Snackbar open={Boolean(successMessage)} autoHideDuration={6000} onClose={() => setSuccessMessage('')}>
        <Alert onClose={() => setSuccessMessage('')} severity="success">
          {successMessage}
        </Alert>
      </Snackbar>
      <Snackbar open={Boolean(errorMessage)} autoHideDuration={6000} onClose={() => setErrorMessage('')}>
        <Alert onClose={() => setErrorMessage('')} severity="error">
          {errorMessage}
        </Alert>
      </Snackbar>
    </Container>
  );
};

export default CardForm;
