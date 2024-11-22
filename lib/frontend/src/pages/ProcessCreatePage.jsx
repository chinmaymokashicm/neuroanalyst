import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';

const ProcessCreatePage = () => {
  const [process, setProcess] = useState({ name: '', status: '' });
  const navigate = useNavigate();

  const handleChange = (e) => {
    const { name, value } = e.target;
    setProcess({ ...process, [name]: value });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    // Send the process data to your API (example URL, adjust as needed)
    fetch('http://localhost:8000/api/processes', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(process),
    })
      .then((response) => response.json())
      .then(() => {
        navigate('/processes'); // Redirect to ProcessPage after creating
      });
  };

  return (
    <div>
      <h1>Create Process</h1>
      <form onSubmit={handleSubmit}>
        <label>
          Name:
          <input
            type="text"
            name="name"
            value={process.name}
            onChange={handleChange}
          />
        </label>
        <br />
        <label>
          Status:
          <input
            type="text"
            name="status"
            value={process.status}
            onChange={handleChange}
          />
        </label>
        <br />
        <button type="submit">Create Process</button>
      </form>
    </div>
  );
};

export default ProcessCreatePage;
