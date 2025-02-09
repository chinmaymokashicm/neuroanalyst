import React, { useEffect, useState } from 'react';
import { Button, Typography, Box, CircularProgress } from '@mui/material';
import DataTable from '../components/DataTable';
import LogViewer from '../components/LogViewer';
import axios from 'axios';
import DynamicForm from '../components/DynamicForm';

const ProcessPage = () => {
  const [processImageTableData, setProcessImageTableData] = useState([]);
  const [processExecTableData, setProcessExecTableData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchProcessImageTableData = async () => {
      try {
        const response = await axios.get('http://localhost:8000/process/image/all');
        setProcessImageTableData(response.data);
        setLoading(false);
      } catch (err) {
        console.log(err);
        setError(err.message || 'Failed to fetch data');
        setLoading(false);
      }
    };

    fetchProcessImageTableData();
  }, []);

  useEffect(() => {
    const fetchProcessExecTableData = async () => {
      try {
        const response = await axios.get('http://localhost:8000/process/exec/all');
        setProcessExecTableData(response.data);
        setLoading(false);
      } catch (err) {
        console.log(err);
        setError(err.message || 'Failed to fetch data');
        setLoading(false);
      }
    };

    fetchProcessExecTableData();
  }, []);

  return (
    <Box sx={{ padding: 2 }}>
      <Typography variant="h4" gutterBottom>
        Processes
      </Typography>
      <Button variant="contained" color="primary" sx={{ marginBottom: 2 }}>
        Create Process
      </Button>

      {/* Display loading spinner, error, or the table */}
      <Typography variant="h6" gutterBottom>
        Process Images
      </Typography>
      {loading ? (
        <CircularProgress />
      ) : error ? (
        <Typography color="error">{error}</Typography>
      ) : (
        <DataTable rows={processImageTableData} />
      )}

      <Typography variant="h6" gutterBottom>
        Process Execution Plans
      </Typography>
      {loading ? (
        <CircularProgress />
      ) : error ? (
        <Typography color="error">{error}</Typography>
      ) : (
        <DataTable rows={processExecTableData} />
      )}

      <DynamicForm
        apiUrl="http://localhost:8000/process/image/schema"
        formName="Create new Process" 
        formDescription="Create a new Process image" 
        submitUrl="http://localhost:8000/process/image/create"
        previewUrl="http://localhost:8000/process/image/preview"
      />

      {/* <LogViewer wsUrl="ws://localhost:8000/ws/log" /> */}
    </Box>
  );
};

export default ProcessPage;
