import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';

const PipelineView = () => {
  const { id } = useParams(); // Extract pipeline ID from URL
  const [pipeline, setPipeline] = useState(null);

  useEffect(() => {
    // Fetch pipeline details based on the ID from your API (example URL, adjust as needed)
    fetch(`http://localhost:8000/api/pipelines/${id}`)
      .then((response) => response.json())
      .then((data) => setPipeline(data));
  }, [id]);

  if (!pipeline) {
    return <div>Loading...</div>;
  }

  return (
    <div>
      <h1>Pipeline: {pipeline.name}</h1>
      <h2>Status: {pipeline.status}</h2>
      <h3>Steps:</h3>
      <ul>
        {pipeline.steps.map((step, index) => (
          <li key={index}>
            <h4>Step {index + 1}: {step.name}</h4>
            <ul>
              {step.processes.map((process) => (
                <li key={process.id}>{process.name} - {process.status}</li>
              ))}
            </ul>
          </li>
        ))}
      </ul>
    </div>
  );
};

export default PipelineView;
