import React from 'react';
import { DataGrid } from '@mui/x-data-grid';

const DataTable = ({ rows }) => {
  if (!rows || rows.length === 0) {
    return <div>No data available</div>;
  }

  // Dynamically generate columns based on keys from the first row
  const columns = Object.keys(rows[0]).map((key) => ({
    field: key,
    headerName: key.replace(/_/g, ' ').toUpperCase(), // Format field names (optional)
    width: 150, // Default column width
    flex: 1, // Allow flexible resizing
  }));

  return (
    <div style={{ height: 400, width: '100%' }}>
      <DataGrid 
        rows={rows} 
        columns={columns} 
        pageSize={5} 
        getRowId={(row) => row.id || row[Object.keys(row)[0]]} // Use `id` or the first key as fallback
        disableSelectionOnClick 
      />
    </div>
  );
};

export default DataTable;
