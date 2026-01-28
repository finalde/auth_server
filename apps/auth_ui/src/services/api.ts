import axios, { AxiosError } from 'axios';
import * as toastr from 'toastr';
import type {
  Client,
  CreateClient,
  UpdateClient,
  User,
  CreateUser,
  UpdateUser,
  Resource,
  CreateResource,
  UpdateResource,
  Scope,
  CreateScope,
  UserClaim,
  CreateUserClaim,
  UpdateUserClaim,
  UserScope,
  CreateUserScope,
  UpdateUserScope,
} from '../types';

// Configure toastr
toastr.options = {
  closeButton: true,
  debug: false,
  newestOnTop: true,
  progressBar: true,
  positionClass: 'toast-top-right',
  preventDuplicates: true,
  onclick: null,
  showDuration: '300',
  hideDuration: '1000',
  timeOut: '5000',
  extendedTimeOut: '1000',
  showEasing: 'swing',
  hideEasing: 'linear',
  showMethod: 'fadeIn',
  hideMethod: 'fadeOut',
};

// Auth Server WebAPI is the resource for AuthUI
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

// Helper function to extract error message from API response
function getErrorMessage(error: AxiosError): string {
  if (error.response?.data) {
    const data = error.response.data as any;
    if (data.detail) {
      return data.detail;
    }
    if (data.message) {
      return data.message;
    }
    if (typeof data === 'string') {
      return data;
    }
  }
  
  // Default messages based on status code
  if (error.response?.status === 403) {
    return "You don't have permission to perform this action. Admin access required.";
  }
  if (error.response?.status === 401) {
    return 'Authentication required. Please log in.';
  }
  if (error.response?.status === 404) {
    return 'Resource not found.';
  }
  if (error.response?.status === 500) {
    return 'Server error. Please try again later.';
  }
  
  return error.message || 'An error occurred. Please try again.';
}

// Handle errors
api.interceptors.response.use(
  (response) => response,
  (error: AxiosError) => {
    const status = error.response?.status;
    const message = getErrorMessage(error);
    
    if (status === 401) {
      // Unauthorized - clear token and redirect to login
      toastr.error('Session expired. Please log in again.', 'Authentication Required');
      localStorage.removeItem('access_token');
      window.location.href = '/login';
    } else if (status === 403) {
      // Forbidden - show permission error
      toastr.error(message, 'Permission Denied');
    } else {
      // Other errors - show error message
      toastr.error(message, 'Error');
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

// User Claims API
export const userClaimsApi = {
  getAll: async (): Promise<UserClaim[]> => {
    const response = await api.get<UserClaim[]>('/user-claims');
    return response.data;
  },
  create: async (data: CreateUserClaim): Promise<UserClaim> => {
    const response = await api.post<UserClaim>('/user-claims', data);
    return response.data;
  },
  update: async (
    userId: string,
    claimName: string,
    data: UpdateUserClaim
  ): Promise<UserClaim> => {
    const response = await api.put<UserClaim>(`/user-claims/${userId}/${claimName}`, data);
    return response.data;
  },
  delete: async (userId: string, claimName: string): Promise<void> => {
    await api.delete(`/user-claims/${userId}/${claimName}`);
  },
};

// User Scopes API
export const userScopesApi = {
  getAll: async (): Promise<UserScope[]> => {
    const response = await api.get<UserScope[]>('/user-scopes');
    return response.data;
  },
  create: async (data: CreateUserScope): Promise<UserScope> => {
    const response = await api.post<UserScope>('/user-scopes', data);
    return response.data;
  },
  update: async (
    userId: string,
    scopeName: string,
    data: UpdateUserScope
  ): Promise<UserScope> => {
    const response = await api.put<UserScope>(`/user-scopes/${userId}/${scopeName}`, data);
    return response.data;
  },
  delete: async (userId: string, scopeName: string): Promise<void> => {
    await api.delete(`/user-scopes/${userId}/${scopeName}`);
  },
};
