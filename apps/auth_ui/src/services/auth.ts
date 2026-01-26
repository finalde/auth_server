import axios from 'axios';

const AUTH_SERVER_URL = 'http://localhost:8000';
const CLIENT_ID = 'auth_ui';
const REDIRECT_URI = 'http://localhost:3001/callback';

// Generate PKCE code verifier and challenge
function generateCodeVerifier(): string {
  const array = new Uint8Array(32);
  crypto.getRandomValues(array);
  return btoa(String.fromCharCode(...array))
    .replace(/\+/g, '-')
    .replace(/\//g, '_')
    .replace(/=/g, '');
}

async function generateCodeChallenge(verifier: string): Promise<string> {
  const encoder = new TextEncoder();
  const data = encoder.encode(verifier);
  const digest = await crypto.subtle.digest('SHA-256', data);
  return btoa(String.fromCharCode(...new Uint8Array(digest)))
    .replace(/\+/g, '-')
    .replace(/\//g, '_')
    .replace(/=/g, '');
}

export async function initiateLogin(): Promise<void> {
  // Generate PKCE pair
  const codeVerifier = generateCodeVerifier();
  const codeChallenge = await generateCodeChallenge(codeVerifier);
  
  // Store code verifier for later
  localStorage.setItem('code_verifier', codeVerifier);
  
  // Build authorization URL - request admin scopes
  const params = new URLSearchParams({
    response_type: 'code',
    client_id: CLIENT_ID,
    redirect_uri: REDIRECT_URI,
    scope: 'openid manage.clients manage.users manage.resources manage.scopes admin',
    code_challenge: codeChallenge,
    code_challenge_method: 'S256',
    state: 'random_state_' + Math.random().toString(36).substring(7)
  });
  
  const authUrl = `${AUTH_SERVER_URL}/api/v1/auth/authorization?${params.toString()}`;
  window.location.href = authUrl;
}

export async function exchangeCodeForToken(code: string): Promise<string> {
  const codeVerifier = localStorage.getItem('code_verifier');
  if (!codeVerifier) {
    throw new Error('Code verifier not found');
  }
  
  const params = new URLSearchParams({
    grant_type: 'authorization_code',
    code: code,
    redirect_uri: REDIRECT_URI,
    client_id: CLIENT_ID,
    code_verifier: codeVerifier
  });
  
  const response = await axios.post(
    `${AUTH_SERVER_URL}/api/v1/auth/token`,
    params.toString(),
    {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
    }
  );
  
  const accessToken = response.data.access_token;
  localStorage.setItem('access_token', accessToken);
  if (response.data.refresh_token) {
    localStorage.setItem('refresh_token', response.data.refresh_token);
  }
  localStorage.removeItem('code_verifier');
  
  return accessToken;
}

export function logout(): void {
  localStorage.removeItem('access_token');
  localStorage.removeItem('refresh_token');
  localStorage.removeItem('code_verifier');
  window.location.href = '/';
}

export function isAuthenticated(): boolean {
  return !!localStorage.getItem('access_token');
}

export function getAccessToken(): string | null {
  return localStorage.getItem('access_token');
}
