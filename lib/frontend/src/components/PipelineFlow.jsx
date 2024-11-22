import React from 'react';
import ReactFlow from 'react-flow-renderer';

const PipelineFlow = ({ elements }) => {
  return (
    <div style={{ height: 500 }}>
      <ReactFlow elements={elements} />
    </div>
  );
};

export default PipelineFlow;
