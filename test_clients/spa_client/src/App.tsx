import React, { useEffect, useState } from 'react';
import { BrowserRouter, Routes, Route, useNavigate, useSearchParams } from 'react-router-dom';
import axios from 'axios';

const AUTH_SERVER_URL = 'http://localhost:8000';
const RESOURCE_SERVER_URL = 'http://localhost:8001';
const CLIENT_ID = 'spa_client';
const REDIRECT_URI = 'http://localhost:3000/callback';

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

function Home() {
  const navigate = useNavigate();
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [userInfo, setUserInfo] = useState<any>(null);
  const [resourceData, setResourceData] = useState<any>(null);

  useEffect(() => {
    // Check if we have tokens in localStorage
    const accessToken = localStorage.getItem('access_token');
    if (accessToken) {
      setIsAuthenticated(true);
      fetchUserInfo(accessToken);
      fetchResourceData(accessToken);
    }
  }, []);

  const handleLogin = async () => {
    // Generate PKCE pair
    const codeVerifier = generateCodeVerifier();
    const codeChallenge = await generateCodeChallenge(codeVerifier);
    
    // Store code verifier for later
    localStorage.setItem('code_verifier', codeVerifier);
    
    // Build authorization URL
    const params = new URLSearchParams({
      response_type: 'code',
      client_id: CLIENT_ID,
      redirect_uri: REDIRECT_URI,
      scope: 'openid profile',
      code_challenge: codeChallenge,
      code_challenge_method: 'S256',
      state: 'random_state_' + Math.random().toString(36).substring(7)
    });
    
    const authUrl = `${AUTH_SERVER_URL}/api/v1/auth/authorization?${params.toString()}`;
    window.location.href = authUrl;
  };

  const fetchUserInfo = async (accessToken: string) => {
    try {
      const response = await axios.get(`${AUTH_SERVER_URL}/api/v1/auth/userinfo`, {
        headers: { Authorization: `Bearer ${accessToken}` }
      });
      setUserInfo(response.data);
    } catch (error) {
      console.error('Failed to fetch user info:', error);
    }
  };

  const fetchResourceData = async (accessToken: string) => {
    try {
      const response = await axios.get(`${RESOURCE_SERVER_URL}/api/data`, {
        headers: { Authorization: `Bearer ${accessToken}` }
      });
      setResourceData(response.data);
    } catch (error) {
      console.error('Failed to fetch resource data:', error);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('code_verifier');
    setIsAuthenticated(false);
    setUserInfo(null);
    setResourceData(null);
  };

  return (
    <div style={{ padding: '20px', maxWidth: '800px', margin: '0 auto' }}>
      <h1>React SPA Client</h1>
      <p>Testing OAuth2 Authorization Code Flow with PKCE</p>
      
      {!isAuthenticated ? (
        <div>
          <button onClick={handleLogin} style={{ padding: '10px 20px', fontSize: '16px' }}>
            Login with OAuth2
          </button>
        </div>
      ) : (
        <div>
          <button onClick={handleLogout} style={{ padding: '10px 20px', fontSize: '16px', marginBottom: '20px' }}>
            Logout
          </button>
          
          <div style={{ marginTop: '20px' }}>
            <h2>User Info</h2>
            <pre>{JSON.stringify(userInfo, null, 2)}</pre>
          </div>
          
          <div style={{ marginTop: '20px' }}>
            <h2>Protected Resource Data</h2>
            <pre>{JSON.stringify(resourceData, null, 2)}</pre>
          </div>
        </div>
      )}
    </div>
  );
}

function Callback() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const code = searchParams.get('code');
    const errorParam = searchParams.get('error');
    
    if (errorParam) {
      setError(`Authorization error: ${errorParam}`);
      return;
    }
    
    if (!code) {
      setError('No authorization code received');
      return;
    }
    
    // Exchange code for tokens
    const codeVerifier = localStorage.getItem('code_verifier');
    if (!codeVerifier) {
      setError('Code verifier not found');
      return;
    }
    
    const exchangeToken = async () => {
      try {
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
        
        // Store tokens
        localStorage.setItem('access_token', response.data.access_token);
        if (response.data.refresh_token) {
          localStorage.setItem('refresh_token', response.data.refresh_token);
        }
        localStorage.removeItem('code_verifier');
        
        // Redirect to home
        navigate('/');
      } catch (err: any) {
        setError(`Token exchange failed: ${err.response?.data?.error || err.message}`);
      }
    };
    
    exchangeToken();
  }, [searchParams, navigate]);

  if (error) {
    return (
      <div style={{ padding: '20px' }}>
        <h2>Error</h2>
        <p>{error}</p>
        <button onClick={() => navigate('/')}>Go Home</button>
      </div>
    );
  }

  return (
    <div style={{ padding: '20px' }}>
      <p>Processing authorization...</p>
    </div>
  );
}

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/callback" element={<Callback />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
