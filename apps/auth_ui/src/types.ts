export interface Client {
  client_id: string;
  client_name?: string;
  client_uri?: string;
  redirect_uris: string[];
  grant_types: string[];
  response_types: string[];
  scopes: string[];
  logo_uri?: string;
  tos_uri?: string;
  policy_uri?: string;
  is_active: boolean;
}

export interface CreateClient {
  client_name?: string;
  client_uri?: string;
  redirect_uris: string[];
  grant_types: string[];
  response_types: string[];
  scopes: string[];
  logo_uri?: string;
  tos_uri?: string;
  policy_uri?: string;
}

export interface UpdateClient {
  client_name?: string;
  client_uri?: string;
  redirect_uris?: string[];
  grant_types?: string[];
  response_types?: string[];
  scopes?: string[];
  logo_uri?: string;
  tos_uri?: string;
  policy_uri?: string;
  is_active?: boolean;
}

export interface User {
  user_id: string;
  username: string;
  email: string;
  status: string;
  first_name?: string;
  last_name?: string;
  is_active: boolean;
}

export interface CreateUser {
  username: string;
  email: string;
  password: string;
  first_name?: string;
  last_name?: string;
}

export interface UpdateUser {
  username?: string;
  email?: string;
  first_name?: string;
  last_name?: string;
  status?: string;
  is_active?: boolean;
}

export interface Resource {
  resource_id: string;
  resource_name: string;
  resource_uri: string;
  scopes: string[];
  description?: string;
  is_active: boolean;
}

export interface CreateResource {
  resource_name: string;
  resource_uri: string;
  scopes: string[];
  description?: string;
}

export interface UpdateResource {
  resource_name?: string;
  resource_uri?: string;
  scopes?: string[];
  description?: string;
  is_active?: boolean;
}

export interface Scope {
  scope_name: string;
  description?: string;
  is_active: boolean;
}

export interface CreateScope {
  scope_name: string;
  description?: string;
}
