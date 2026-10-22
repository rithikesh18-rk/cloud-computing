/**
 * Typed API Client for CloudPulse AI.
 * Communicates with FastAPI backend with automatic base URL and error handling.
 */

import axios, { AxiosInstance } from 'axios';
import {
  HealthResponse,
  DatasetPreviewResponse,
  DatasetUploadResponse,
  TrainModelRequest,
  TrainModelResponse,
  PredictRequest,
  PredictResponse,
  SimulationRunRequest,
  SimulationComparisonResponse,
  SimulationHistoryItem,
  SettingsUpdate,
  SettingsResponse,
} from '../types';

// Use relative URL to leverage Vite proxy, falling back to direct FastAPI URL
const BASE_URL = import.meta.env.VITE_API_URL || '/api';

export const apiClient: AxiosInstance = axios.create({
  baseURL: BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000,
});

export const api = {
  // Health
  getHealth: async (): Promise<HealthResponse> => {
    const res = await apiClient.get<HealthResponse>('/health');
    return res.data;
  },

  // Dataset
  getDatasetPreview: async (): Promise<DatasetPreviewResponse> => {
    const res = await apiClient.get<DatasetPreviewResponse>('/dataset/preview');
    return res.data;
  },

  uploadDataset: async (file: File): Promise<DatasetUploadResponse> => {
    const formData = new FormData();
    formData.append('file', file);
    const res = await apiClient.post<DatasetUploadResponse>('/dataset/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return res.data;
  },

  getSampleDatasetUrl: (): string => {
    return `${BASE_URL}/dataset/sample`;
  },

  // Forecasting
  trainForecaster: async (params?: TrainModelRequest): Promise<TrainModelResponse> => {
    const res = await apiClient.post<TrainModelResponse>('/forecast/train', params || {});
    return res.data;
  },

  predictForecast: async (horizon_steps: number = 6): Promise<PredictResponse> => {
    const payload: PredictRequest = { horizon_steps };
    const res = await apiClient.post<PredictResponse>('/forecast/predict', payload);
    return res.data;
  },

  // Simulation
  runSimulation: async (params: SimulationRunRequest): Promise<SimulationComparisonResponse> => {
    const res = await apiClient.post<SimulationComparisonResponse>('/simulation/run', params);
    return res.data;
  },

  getSimulationHistory: async (limit: number = 20): Promise<SimulationHistoryItem[]> => {
    const res = await apiClient.get<SimulationHistoryItem[]>(`/simulation/history?limit=${limit}`);
    return res.data;
  },

  getSimulationExportUrl: (simulationId: number): string => {
    return `${BASE_URL}/simulation/export/${simulationId}`;
  },

  // Settings
  getSettings: async (): Promise<SettingsResponse> => {
    const res = await apiClient.get<SettingsResponse>('/settings');
    return res.data;
  },

  updateSettings: async (payload: SettingsUpdate): Promise<SettingsResponse> => {
    const res = await apiClient.put<SettingsResponse>('/settings', payload);
    return res.data;
  },
};

export default api;
