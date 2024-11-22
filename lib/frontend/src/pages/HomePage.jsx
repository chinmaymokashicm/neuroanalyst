import React from 'react';
import { Card, CardContent, Typography, Button, Grid2, Box } from '@mui/material';
import { Link } from 'react-router-dom';

const HomePage = () => {
  return (
    <Box sx={{ marginTop: 4 }}>
      <Grid2 container spacing={4}>
        <Grid2 item xs={12} sm={6} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h5" gutterBottom>
                Data Analysis
              </Typography>
              <Typography variant="body2" color="textSecondary">
                Manage your neuroimaging analysis processes and track progress.
              </Typography>
              <Button variant="contained" color="primary" component={Link} to="/processes" sx={{ marginTop: 2 }}>
                View Processes
              </Button>
            </CardContent>
          </Card>
        </Grid2>
        <Grid2 item xs={12} sm={6} md={4}>
          <Card>
            <CardContent>
              <Typography variant="h5" gutterBottom>
                Pipelines
              </Typography>
              <Typography variant="body2" color="textSecondary">
                Explore and manage your data analysis pipelines.
              </Typography>
              <Button variant="contained" color="primary" component={Link} to="/pipelines" sx={{ marginTop: 2 }}>
                View Pipelines
              </Button>
            </CardContent>
          </Card>
        </Grid2>
      </Grid2>
    </Box>
  );
};

export default HomePage;
