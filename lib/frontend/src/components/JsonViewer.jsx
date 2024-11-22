import React from 'react';
import ReactJson from 'react-json-view';

const JsonViewer = ({ data }) => {
  return <ReactJson src={data} theme="monokai" collapsed={2} />;
};

export default JsonViewer;
