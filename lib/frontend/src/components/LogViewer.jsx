import React, { useEffect, useState, useRef } from "react";
import { Box, Typography, Paper, CircularProgress, Button, IconButton} from "@mui/material";
import ArrowUpwardIcon from "@mui/icons-material/ArrowUpward";
import ArrowDownwardIcon from "@mui/icons-material/ArrowDownward";

const LogViewer = ({ wsUrl }) => {
    const [logs, setLogs] = useState("");
    const [loading, setLoading] = useState(true);
    const logContainerRef = useRef(null);

    useEffect(() => {
        const socket = new WebSocket(wsUrl);

        socket.onopen = () => {
            console.log("WebSocket connection established");
            setLoading(false);
        };

        socket.onmessage = (event) => {
            // setLogs((prevLogs) => prevLogs + event.data + "\n");
            setLogs((event.data));
            scrollToBottom();
        };

        socket.onclose = () => {
            console.log("WebSocket connection closed");
        };

        socket.onerror = (error) => {
            console.error("WebSocket error:", error);
        };

        const scrollToBottom = () => {
            if (logContainerRef.current) {
                logContainerRef.current.scrollTop = logContainerRef.current.scrollHeight;
            }
        };

        return () => socket.close();
    }, [wsUrl]);

    const scrollToTop = () => {
        if (logContainerRef.current) {
            logContainerRef.current.scrollTop = 0;
        }
    };

    const scrollToBottom = () => {
        if (logContainerRef.current) {
            logContainerRef.current.scrollTop = logContainerRef.current.scrollHeight;
        }
    };

return (
    <Box sx={{ marginTop: 4, padding: 2, position: "relative" }}>
        <Typography variant="h5" gutterBottom>
            Log Viewer
        </Typography>
        {loading ? (
            <CircularProgress />
        ) : (
            <Paper
                sx={{
                    padding: 2,
                    maxHeight: 400,
                    overflowY: "scroll",
                    backgroundColor: "#f5f5f5",
                    whiteSpace: "pre-wrap",
                }}
                ref={logContainerRef}
            >
                <div dangerouslySetInnerHTML={{ __html: logs || "No logs yet..." }} />
            </Paper>
        )}

        {/* Scroll buttons */}
        <Box
            sx={{
                position: "fixed",
                bottom: 20,
                right: 20,
                display: "flex",
                flexDirection: "column",
                gap: 1,
            }}
        >
            <IconButton
                size="medium"
                color="primary"
                onClick={scrollToTop}
                title="Scroll to Top"
            >
                <ArrowUpwardIcon />
            </IconButton>
            <IconButton
                size="medium"
                color="primary"
                onClick={scrollToBottom}
                title="Scroll to Bottom"
            >
                <ArrowDownwardIcon />
            </IconButton>
        </Box>
    </Box>
);
};

export default LogViewer;
