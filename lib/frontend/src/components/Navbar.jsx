import React from 'react';
import { AppBar, Toolbar, Typography, Button, Container } from '@mui/material';
import { Link } from 'react-router-dom';

const Navbar = () => {
  return (
    <AppBar position="sticky" color="primary">
      <Toolbar>
        <Container>
          <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
            NeuroAnalyst: Data Analysis and Knowledge Discovery
          </Typography>
          <Button color="inherit" component={Link} to="/">Home</Button>
          <Button color="inherit" component={Link} to="/processes">Processes</Button>
          <Button color="inherit" component={Link} to="/pipelines">Pipelines</Button>
        </Container>
      </Toolbar>
    </AppBar>
  );
};

export default Navbar;
