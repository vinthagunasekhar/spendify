import axios from 'axios';

const API_BASE_URL = 'http://localhost:5000'; // Replace with your Flask app's base URL if different

export const getAvailableCards = () => axios.get(`${API_BASE_URL}/available-cards`);
export const getBillingDates = () => axios.get(`${API_BASE_URL}/billing-dates`);
export const addCard = (cardData) => axios.post(`${API_BASE_URL}/add-card`, cardData);
export const getUserCards = () => axios.get(`${API_BASE_URL}/user-cards`);
export const getStrategy = () => axios.get(`${API_BASE_URL}/strategy`);
