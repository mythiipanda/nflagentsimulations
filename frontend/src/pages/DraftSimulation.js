import React, { useState } from 'react';

function DraftSimulation() {
  const [draftOrder, setDraftOrder] = useState([]);

  const generateDraftOrder = () => {
    const people = ['Person 1', 'Person 2', 'Person 3', 'Person 4', 'Person 5']; // Replace with actual people
    const shuffledPeople = people.sort(() => 0.5 - Math.random());
    setDraftOrder(shuffledPeople);
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-4">Mock Draft Simulation</h1>
      <button
        className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded"
        onClick={generateDraftOrder}
      >
        Generate Draft Order
      </button>
      {draftOrder.length > 0 && (
        <ul className="mt-4">
          {draftOrder.map((person, index) => (
            <li key={index} className="mb-2">
              Pick {index + 1}: {person}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

export default DraftSimulation;
