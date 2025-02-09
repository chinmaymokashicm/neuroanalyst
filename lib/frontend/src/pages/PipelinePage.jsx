import React from 'react';
import { Button, Typography, Box } from '@mui/material';
import LogViewer from '../components/LogViewer';

const PipelinePage = () => {
  return (
    <Box sx={{ padding: 2 }}>
      <Typography variant="h4" gutterBottom>
        Processes
      </Typography>
      <Button variant="contained" color="primary" sx={{ marginBottom: 2 }}>
        Create Pipeline
      </Button>
      {/* Add your process list or cards here */}
      <LogViewer wsUrl="ws://localhost:8000/ws/log" />
    </Box>
  );
};

export default PipelinePage;
