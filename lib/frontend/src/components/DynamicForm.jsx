import React, { useState, useEffect } from "react";
import {
    Box,
    Button,
    TextField,
    Typography,
    Dialog,
    DialogTitle,
    DialogContent,
    DialogActions,
    CircularProgress,
    Paper,
} from "@mui/material";
import axios from "axios";

const DynamicForm = ({ apiUrl, formName, formDescription, submitUrl, previewUrl }) => {
    const [schema, setSchema] = useState(null); // Form schema fetched from API
    const [formData, setFormData] = useState({}); // Form data state
    const [loading, setLoading] = useState(true); // Loading state
    const [error, setError] = useState(null); // Error state
    const [isPreviewOpen, setIsPreviewOpen] = useState(false);
    const [previewData, setPreviewData] = useState(null); // Data from the preview endpoint
    const [previewLoading, setPreviewLoading] = useState(false); // Preview loading state
    const [previewError, setPreviewError] = useState(null); // Preview error state
    const [isDialogOpen, setIsDialogOpen] = useState(false);
    const [submitDialogContent, setSubmitDialogContent] = useState(null);
    const [isLoading, setIsLoading] = useState(false);

    // Fetch form schema from API
    useEffect(() => {
        const fetchSchema = async () => {
            try {
                const response = await axios.get(apiUrl);
                setSchema(response.data);
                // Initialize form data with default values
                const initialFormData = response.data.fields.reduce((acc, field) => {
                    acc[field.name] = field.default !== undefined ? field.default : ""; // Use default value if available
                    return acc;
                }, {});
                setFormData(initialFormData);
                setLoading(false);
            } catch (err) {
                setError("Failed to load form schema");
                setLoading(false);
            }
        };
        fetchSchema();
    }, [apiUrl]);

    // Handle input changes
    const handleChange = (fieldName, value) => {
        setFormData((prev) => ({ ...prev, [fieldName]: value }));
    };

    // Fetch preview data from the preview endpoint
    const handlePreviewSubmit = async (event) => {
        event.preventDefault();
        setPreviewLoading(true);
        setPreviewError(null);
        try {
            const formDataObj = new FormData();
            formDataObj.append("form_data", JSON.stringify(formData)); // Convert formData to JSON string and append it

            const response = await axios.post(previewUrl, formDataObj, {
                headers: {
                    "Content-Type": "multipart/form-data",
                },
            });
            setPreviewData(response.data);
            setIsPreviewOpen(true);
        } catch (error) {
            console.error("Error fetching preview data:", error);
            setPreviewError("Failed to fetch preview data. Please try again.");
        } finally {
            setPreviewLoading(false);
        }
    };

    const handleFinalSubmit = async (event) => {
        event.preventDefault();
        setIsDialogOpen(true);
        setIsLoading(true);
        try {
            const formDataObj = new FormData();
            formDataObj.append("form_data", JSON.stringify(previewData)); // Convert formData to JSON string and append it

            const response = await axios.post(submitUrl, formDataObj, {
                headers: {
                    "Content-Type": "multipart/form-data",
                },
            });
            setSubmitDialogContent({
                type: "success",
                message: response.data.message,
            })
            setIsPreviewOpen(false);
        } catch (error) {
            console.error("Error submitting form:", error);
            setSubmitDialogContent({
                type: "error",
                message: error.response?.data?.message || "Failed to submit form. Please try again.",
            })
        } finally {
            setIsLoading(false);
        }
    };

    const handleCancelPreview = () => {
        setIsPreviewOpen(false);
    };

    const handleDialogClose = () => {
        setIsDialogOpen(false);
        setSubmitDialogContent(null);
    };

    if (loading) {
        return <Typography>Loading...</Typography>;
    }

    if (error) {
        return <Typography color="error">{error}</Typography>;
    }

    return (
        <Box component="form" onSubmit={handlePreviewSubmit} sx={{ padding: 2 }}>
            <Typography variant="h5" gutterBottom>
                {formName}<br />
                {/* {formDescription && ` - ${formDescription}`} */}
                {formDescription}
            </Typography>
            {schema.fields.map((field) => {
                if (field.type === "str") {
                    return (
                        <TextField
                            key={field.name}
                            fullWidth
                            label={field.description || field.name}
                            value={formData[field.name]}
                            onChange={(e) => handleChange(field.name, e.target.value)}
                            required={field.required}
                            sx={{ marginBottom: 2 }}
                        />
                    );
                }
                if (field.type === "list") {
                    return (
                        <Box key={field.name} sx={{ marginBottom: 3 }}>
                            <Typography variant="subtitle1">{field.description}</Typography>
                            {Array.isArray(formData[field.name]) &&
                                formData[field.name].map((item, index) => (
                                    <Box
                                        key={index}
                                        sx={{
                                            display: "flex",
                                            alignItems: "center",
                                            gap: 1,
                                            marginBottom: 1,
                                        }}
                                    >
                                        <TextField
                                            fullWidth
                                            value={item}
                                            onChange={(e) => {
                                                const updatedList = [...formData[field.name]];
                                                updatedList[index] = e.target.value;
                                                handleChange(field.name, updatedList);
                                            }}
                                            placeholder={`Item ${index + 1}`}
                                        />
                                        <Button
                                            variant="contained"
                                            color="error"
                                            onClick={() => {
                                                const updatedList = [...formData[field.name]];
                                                updatedList.splice(index, 1);
                                                handleChange(field.name, updatedList);
                                            }}
                                        >
                                            -
                                        </Button>
                                    </Box>
                                ))}
                            <Button
                                variant="contained"
                                color="primary"
                                onClick={() => {
                                    const updatedList = [...(formData[field.name] || []), ""];
                                    handleChange(field.name, updatedList);
                                }}
                            >
                                +
                            </Button>
                        </Box>
                    );
                }
                if (field.type === "bool") {
                    return (
                        <TextField
                            key={field.name}
                            fullWidth
                            label={field.description || field.name}
                            value={formData[field.name]}
                            onChange={(e) => handleChange(field.name, e.target.checked)}
                            type="checkbox"
                            required={field.required}
                            sx={{ marginBottom: 2 }}
                        />
                    );
                }
                if (field.type === "file") {
                    return (
                        <Box key={field.name} sx={{ marginBottom: 3 }}>
                            <Typography variant="subtitle1">{field.description}</Typography>
                            <Button
                                variant="outlined"
                                component="label"
                                sx={{ display: "flex", alignItems: "center", padding: 1, justifyContent: "center" }}
                            >
                                Choose File
                                <input
                                    type="file"
                                    hidden
                                    onChange={(e) => handleChange(field.name, e.target.files[0])}
                                />
                            </Button>
                            <Typography variant="caption" color="textSecondary">
                                {formData[field.name]?.name || field.default || "No file selected"}
                            </Typography>
                        </Box>
                    );
                }
                if (field.type === "directory") {
                    return (
                        <Box key={field.name} sx={{ marginBottom: 2 }}>
                            <Typography variant="subtitle1">{field.description || "Choose Directory"}</Typography>
                            <Button
                                variant="outlined"
                                component="label"
                                sx={{ display: "flex", alignItems: "center", padding: 1 }}
                            >
                                Choose Folder
                                <input
                                    type="file"
                                    hidden
                                    webkitdirectory=""
                                    onChange={(e) => {
                                        // Convert the file list to an array of file paths
                                        const filesArray = Array.from(e.target.files).map(file => file.webkitRelativePath);
                                        // Get path of directory
                                        const directoryPath = filesArray[0].split("/").slice(0, -1).join("/");
                                        handleChange(field.name, directoryPath); // Store the directory path
                                    }}
                                />
                            </Button>
                            <Typography variant="caption">
                                {formData[field.name] && formData[field.name].length > 0
                                    ? `Selected directory: ${formData[field.name]}`
                                    : "No files selected"}
                            </Typography>
                        </Box>
                    );
                }
                if (field.type === "dict") {
                    return (
                        <Box key={field.name} sx={{ marginBottom: 3 }}>
                            <Typography variant="subtitle1">{field.description}</Typography>
                            {formData[field.name] &&
                                Object.entries(formData[field.name]).map(([key, value], index) => (
                                    <Box
                                        key={index}
                                        sx={{
                                            display: "flex",
                                            alignItems: "center",
                                            gap: 1,
                                            marginBottom: 1,
                                        }}
                                    >
                                        <TextField
                                            fullWidth
                                            label="Key"
                                            value={key}
                                            onChange={(e) => {
                                                const updatedDict = { ...formData[field.name] };
                                                const newKey = e.target.value;
                                                updatedDict[newKey] = updatedDict[key];
                                                delete updatedDict[key];
                                                handleChange(field.name, updatedDict);
                                            }}
                                        />
                                        <TextField
                                            fullWidth
                                            label="Value"
                                            value={value}
                                            onChange={(e) => {
                                                const updatedDict = { ...formData[field.name] };
                                                updatedDict[key] = e.target.value;
                                                handleChange(field.name, updatedDict);
                                            }}
                                        />
                                        <Button
                                            variant="contained"
                                            color="error"
                                            onClick={() => {
                                                const updatedDict = { ...formData[field.name] };
                                                delete updatedDict[key];
                                                handleChange(field.name, updatedDict);
                                            }}
                                        >
                                            -
                                        </Button>
                                    </Box>
                                ))}
                            <Button
                                variant="contained"
                                color="primary"
                                onClick={() => {
                                    const updatedDict = { ...(formData[field.name] || {}) };
                                    updatedDict[`key-${Object.keys(updatedDict).length}`] = "";
                                    handleChange(field.name, updatedDict);
                                }}
                            >
                                +
                            </Button>
                        </Box>
                    );
                }
                return null; // Handle other field types as needed
            })}
            <Button type="preview" variant="contained" color="secondary">
                Preview
            </Button>
            {/* <Button type="submit" variant="contained" color="primary">
                Submit
            </Button> */}
            <Dialog open={isPreviewOpen} onClose={handleCancelPreview} fullWidth maxWidth="sm">
                <DialogTitle>Preview Your Submission</DialogTitle>
                <DialogContent>
                    {previewError ? (
                        <Typography color="error">{previewError}</Typography>
                    ) : (
                        <Paper sx={{ padding: 2 }}>
                            <pre>{previewData ? JSON.stringify(previewData, null, 2) : "Loading..."}</pre>
                        </Paper>
                    )}
                </DialogContent>
                <DialogActions>
                    <Button onClick={handleCancelPreview} color="secondary">
                        Cancel
                    </Button>
                    <Button
                        onClick={handleFinalSubmit}
                        color="primary"
                        variant="contained"
                        disabled={!previewData}
                    >
                        Submit
                    </Button>
                </DialogActions>
            </Dialog>

            {/* Dialog for Status and Response */}
            <Dialog open={isDialogOpen} onClose={handleDialogClose}>
                <DialogTitle>
                    {isLoading ? "Processing..." : submitDialogContent?.type === "success" ? "Success" : "Error"}
                </DialogTitle>
                <DialogContent>
                    {isLoading ? (
                        <Box display="flex" alignItems="center" justifyContent="center" sx={{ py: 2 }}>
                            <CircularProgress />
                            <Typography ml={2}>Waiting for response...</Typography>
                        </Box>
                    ) : (
                        <Typography>
                            {submitDialogContent?.message}
                        </Typography>
                    )}
                </DialogContent>
                {!isLoading && (
                    <DialogActions>
                        <Button onClick={handleDialogClose} color="primary">
                            Close
                        </Button>
                    </DialogActions>
                )}
            </Dialog>
        </Box>
    );
};

export default DynamicForm;
