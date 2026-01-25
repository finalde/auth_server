import axios from 'axios';
import type { Client, CreateClient, UpdateClient, User, CreateUser, UpdateUser, Resource, CreateResource, UpdateResource, Scope, CreateScope } from '../types';

const API_BASE = 'http://localhost:8000/api/v1';

const api = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Handle errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Unauthorized - clear token and redirect to login
      localStorage.removeItem('access_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Clients API
export const clientsApi = {
  getAll: async (): Promise<Client[]> => {
    const response = await api.get<Client[]>('/clients');
    return response.data;
  },
  getById: async (clientId: string): Promise<Client> => {
    const response = await api.get<Client>(`/clients/${clientId}`);
    return response.data;
  },
  create: async (data: CreateClient): Promise<Client> => {
    const response = await api.post<Client>('/clients', data);
    return response.data;
  },
  update: async (clientId: string, data: UpdateClient): Promise<Client> => {
    const response = await api.put<Client>(`/clients/${clientId}`, data);
    return response.data;
  },
  delete: async (clientId: string): Promise<void> => {
    await api.delete(`/clients/${clientId}`);
  },
};

// Users API
export const usersApi = {
  getAll: async (): Promise<User[]> => {
    const response = await api.get<User[]>('/users');
    return response.data;
  },
  getById: async (userId: string): Promise<User> => {
    const response = await api.get<User>(`/users/${userId}`);
    return response.data;
  },
  create: async (data: CreateUser): Promise<User> => {
    const response = await api.post<User>('/users', data);
    return response.data;
  },
  update: async (userId: string, data: UpdateUser): Promise<User> => {
    const response = await api.put<User>(`/users/${userId}`, data);
    return response.data;
  },
  delete: async (userId: string): Promise<void> => {
    await api.delete(`/users/${userId}`);
  },
};

// Resources API
export const resourcesApi = {
  getAll: async (): Promise<Resource[]> => {
    const response = await api.get<Resource[]>('/resources');
    return response.data;
  },
  getById: async (resourceId: string): Promise<Resource> => {
    const response = await api.get<Resource>(`/resources/${resourceId}`);
    return response.data;
  },
  create: async (data: CreateResource): Promise<Resource> => {
    const response = await api.post<Resource>('/resources', data);
    return response.data;
  },
  update: async (resourceId: string, data: UpdateResource): Promise<Resource> => {
    const response = await api.put<Resource>(`/resources/${resourceId}`, data);
    return response.data;
  },
  delete: async (resourceId: string): Promise<void> => {
    await api.delete(`/resources/${resourceId}`);
  },
};

// Scopes API
export const scopesApi = {
  getAll: async (): Promise<Scope[]> => {
    const response = await api.get<Scope[]>('/scopes');
    return response.data;
  },
  getById: async (scopeName: string): Promise<Scope> => {
    const response = await api.get<Scope>(`/scopes/${scopeName}`);
    return response.data;
  },
  create: async (data: CreateScope): Promise<Scope> => {
    const response = await api.post<Scope>('/scopes', data);
    return response.data;
  },
  update: async (scopeName: string, data: Partial<CreateScope>): Promise<Scope> => {
    const response = await api.put<Scope>(`/scopes/${scopeName}`, data);
    return response.data;
  },
  delete: async (scopeName: string): Promise<void> => {
    await api.delete(`/scopes/${scopeName}`);
  },
};
