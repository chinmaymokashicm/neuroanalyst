import React from "react";
import { Dialog, DialogTitle, DialogContent, DialogActions, Button, Paper } from "@mui/material";

const JSONPreview = ({ open, data, onCancel, onConfirm }) => {
    return (
        <Dialog open={open} onClose={onCancel} fullWidth maxWidth="sm">
            <DialogTitle>Preview Your Submission</DialogTitle>
            <DialogContent>
                <Paper sx={{ padding: 2 }}>
                    <pre>{JSON.stringify(data, null, 2)}</pre>
                </Paper>
            </DialogContent>
            <DialogActions>
                <Button onClick={onCancel} color="secondary">
                    Cancel
                </Button>
                <Button onClick={onConfirm} color="primary" variant="contained">
                    Confirm and Submit
                </Button>
            </DialogActions>
        </Dialog>
    );
};

export default JSONPreview;
