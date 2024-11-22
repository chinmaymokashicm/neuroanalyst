import axios from 'axios';

const API_BASE_URL = "http://localhost:8000";

export const getProcesses = async () => {
  const response = await axios.get(`${API_BASE_URL}/processes`);
  return response.data;
};

export const createProcess = async (data) => {
  const response = await axios.post(`${API_BASE_URL}/processes`, data);
  return response.data;
};

export const updateProcess = async (id, data) => {
  const response = await axios.put(`${API_BASE_URL}/processes/${id}`, data);
  return response.data;
};

export const deleteProcess = async (id) => {
  const response = await axios.delete(`${API_BASE_URL}/processes/${id}`);
  return response.data;
};
