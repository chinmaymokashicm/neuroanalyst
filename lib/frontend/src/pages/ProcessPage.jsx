import React from 'react';
import { Button, Typography, Box } from '@mui/material';

const ProcessPage = () => {
  return (
    <Box sx={{ padding: 2 }}>
      <Typography variant="h4" gutterBottom>
        Processes
      </Typography>
      <Button variant="contained" color="primary" sx={{ marginBottom: 2 }}>
        Create Process
      </Button>
      {/* Add your process list or cards here */}
    </Box>
  );
};

export default ProcessPage;
