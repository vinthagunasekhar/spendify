import React, { useEffect, useState } from 'react';
import { getUserCards } from '../services/api';

const HomePage = () => {
  const [cards, setCards] = useState([]);

  useEffect(() => {
    getUserCards().then(response => setCards(response.data));
  }, []);

  return (
    <div>
      <h2>User Cards</h2>
      <ul>
        {cards.map((card, index) => (
          <li key={index}>{card.name} - {card.limit} - {card.usage}</li>
        ))}
      </ul>
    </div>
  );
};

export default HomePage;
