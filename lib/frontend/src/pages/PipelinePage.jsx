import React from 'react';
import { Button, Typography, Box } from '@mui/material';

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
    </Box>
  );
};

export default PipelinePage;
