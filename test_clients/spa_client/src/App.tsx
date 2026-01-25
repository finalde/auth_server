import React, { useEffect, useState } from 'react';
import { BrowserRouter, Routes, Route, useNavigate, useSearchParams } from 'react-router-dom';
import axios from 'axios';

const AUTH_SERVER_URL = 'http://localhost:8000';
const RESOURCE_SERVER_URL = 'http://localhost:8001';
const CLIENT_ID = 'spa_client';
const REDIRECT_URI = 'http://localhost:3000/callback';

// Decode JWT token to see its contents (for debugging)
function decodeJWT(token: string): any {
  try {
    const parts = token.split('.');
    if (parts.length !== 3) {
      return { error: 'Invalid JWT format' };
    }
    
    // Decode payload (second part)
    const payload = parts[1];
    // Add padding if needed for base64 decoding
    const paddedPayload = payload + '='.repeat((4 - payload.length % 4) % 4);
    const decoded = atob(paddedPayload);
    return JSON.parse(decoded);
  } catch (error) {
    return { error: 'Failed to decode JWT', details: error };
  }
}

// Print access token details to console
function printAccessToken(token: string) {
  const decoded = decodeJWT(token);
  
  console.log('='.repeat(80));
  console.log('🔐 ACCESS TOKEN DECODED');
  console.log('='.repeat(80));
  console.log('Full Token Payload:', JSON.stringify(decoded, null, 2));
  console.log('');
  
  // Highlight scope claim
  if (decoded.scope) {
    const scopeValue = decoded.scope;
    const scopes = typeof scopeValue === 'string' ? scopeValue.split(' ') : scopeValue;
    console.log('📋 SCOPES IN TOKEN:', scopes);
    console.log('   - Has "openid":', scopes.includes('openid'));
    console.log('   - Has "data.read":', scopes.includes('data.read'));
    console.log('   - Has "data.write":', scopes.includes('data.write'));
    console.log('   - Has "read":', scopes.includes('read'));
    console.log('   - Has "write":', scopes.includes('write'));
    console.log('   - Has "admin":', scopes.includes('admin'));
  } else {
    console.log('⚠️  WARNING: No "scope" claim found in token!');
  }
  
  console.log('');
  console.log('Other Claims:');
  console.log('   - sub (subject):', decoded.sub);
  console.log('   - client_id:', decoded.client_id);
  console.log('   - aud (audience):', decoded.aud);
  console.log('   - iss (issuer):', decoded.iss);
  console.log('   - exp (expires at):', decoded.exp ? new Date(decoded.exp * 1000).toISOString() : 'N/A');
  console.log('   - iat (issued at):', decoded.iat ? new Date(decoded.iat * 1000).toISOString() : 'N/A');
  console.log('='.repeat(80));
}

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
  const [endpointResults, setEndpointResults] = useState<any>({
    public: null,
    read: null,
    write: null
  });
  const [loading, setLoading] = useState<{[key: string]: boolean}>({
    public: false,
    read: false,
    write: false
  });

  useEffect(() => {
    // Check if we have tokens in localStorage
    const accessToken = localStorage.getItem('access_token');
    if (accessToken) {
      setIsAuthenticated(true);
      // Print token details to console for debugging
      printAccessToken(accessToken);
      fetchUserInfo(accessToken);
    }
  }, []);

  const handleLogin = async () => {
    // Generate PKCE pair
    const codeVerifier = generateCodeVerifier();
    const codeChallenge = await generateCodeChallenge(codeVerifier);
    
    // Store code verifier for later
    localStorage.setItem('code_verifier', codeVerifier);
    
    // Build authorization URL - request all scopes (will be filtered by server based on user)
    const params = new URLSearchParams({
      response_type: 'code',
      client_id: CLIENT_ID,
      redirect_uri: REDIRECT_URI,
      scope: 'openid data.read data.write admin',
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

  const callPublicEndpoint = async () => {
    setLoading(prev => ({ ...prev, public: true }));
    try {
      const response = await axios.get(`${RESOURCE_SERVER_URL}/public`);
      setEndpointResults(prev => ({ ...prev, public: response.data }));
    } catch (error: any) {
      setEndpointResults(prev => ({ 
        ...prev, 
        public: { error: error.response?.data?.detail || error.message } 
      }));
    } finally {
      setLoading(prev => ({ ...prev, public: false }));
    }
  };

  const callReadEndpoint = async () => {
    const accessToken = localStorage.getItem('access_token');
    if (!accessToken) {
      // Redirect to login
      handleLogin();
      return;
    }
    
    setLoading(prev => ({ ...prev, read: true }));
    try {
      const response = await axios.get(`${RESOURCE_SERVER_URL}/protected/read`, {
        headers: { Authorization: `Bearer ${accessToken}` }
      });
      setEndpointResults(prev => ({ ...prev, read: response.data }));
    } catch (error: any) {
      if (error.response?.status === 401) {
        // Token expired or invalid - redirect to login
        handleLogin();
      } else {
        setEndpointResults(prev => ({ 
          ...prev, 
          read: { error: error.response?.data?.detail || error.message } 
        }));
      }
    } finally {
      setLoading(prev => ({ ...prev, read: false }));
    }
  };

  const callWriteEndpoint = async () => {
    const accessToken = localStorage.getItem('access_token');
    if (!accessToken) {
      // Redirect to login
      handleLogin();
      return;
    }
    
    setLoading(prev => ({ ...prev, write: true }));
    try {
      const response = await axios.get(`${RESOURCE_SERVER_URL}/protected/write`, {
        headers: { Authorization: `Bearer ${accessToken}` }
      });
      setEndpointResults(prev => ({ ...prev, write: response.data }));
    } catch (error: any) {
      if (error.response?.status === 401) {
        // Token expired or invalid - redirect to login
        handleLogin();
      } else {
        setEndpointResults(prev => ({ 
          ...prev, 
          write: { error: error.response?.data?.detail || error.message } 
        }));
      }
    } finally {
      setLoading(prev => ({ ...prev, write: false }));
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('code_verifier');
    setIsAuthenticated(false);
    setUserInfo(null);
    setEndpointResults({ public: null, read: null, write: null });
  };

  return (
    <div style={{ padding: '20px', maxWidth: '1000px', margin: '0 auto' }}>
      <h1>React SPA Client - OAuth2 Test</h1>
      <p>Testing OAuth2 Authorization Code Flow with scope-based access control</p>
      
      {!isAuthenticated ? (
        <div>
          <p>Click the button below to login. You will be redirected to the login page.</p>
          <button onClick={handleLogin} style={{ padding: '10px 20px', fontSize: '16px' }}>
            Login with OAuth2
          </button>
        </div>
      ) : (
        <div>
          <div style={{ marginBottom: '20px', padding: '10px', backgroundColor: '#f0f0f0', borderRadius: '5px' }}>
            <button onClick={handleLogout} style={{ padding: '10px 20px', fontSize: '16px', marginBottom: '10px' }}>
              Logout
            </button>
            <div>
              <h3>User Info</h3>
              <pre style={{ fontSize: '12px', overflow: 'auto' }}>{JSON.stringify(userInfo, null, 2)}</pre>
            </div>
          </div>
          
          <div style={{ marginTop: '30px' }}>
            <h2>Test Endpoints</h2>
            <p>Click the buttons below to test different endpoints on the resource server:</p>
            
            <div style={{ display: 'flex', flexDirection: 'column', gap: '15px', marginTop: '20px' }}>
              <div style={{ border: '1px solid #ccc', padding: '15px', borderRadius: '5px' }}>
                <h3>Button 1: Public Endpoint</h3>
                <p style={{ fontSize: '14px', color: '#666' }}>No authentication required - should always work</p>
                <button 
                  onClick={callPublicEndpoint} 
                  disabled={loading.public}
                  style={{ padding: '10px 20px', fontSize: '16px', marginTop: '10px' }}
                >
                  {loading.public ? 'Loading...' : 'Call Public Endpoint'}
                </button>
                {endpointResults.public && (
                  <pre style={{ marginTop: '10px', fontSize: '12px', overflow: 'auto', backgroundColor: '#f9f9f9', padding: '10px' }}>
                    {JSON.stringify(endpointResults.public, null, 2)}
                  </pre>
                )}
              </div>

              <div style={{ border: '1px solid #ccc', padding: '15px', borderRadius: '5px' }}>
                <h3>Button 2: Protected Read Endpoint</h3>
                <p style={{ fontSize: '14px', color: '#666' }}>Requires 'read' scope - should work for testuser</p>
                <button 
                  onClick={callReadEndpoint} 
                  disabled={loading.read}
                  style={{ padding: '10px 20px', fontSize: '16px', marginTop: '10px' }}
                >
                  {loading.read ? 'Loading...' : 'Call Read Endpoint'}
                </button>
                {endpointResults.read && (
                  <pre style={{ marginTop: '10px', fontSize: '12px', overflow: 'auto', backgroundColor: '#f9f9f9', padding: '10px' }}>
                    {JSON.stringify(endpointResults.read, null, 2)}
                  </pre>
                )}
              </div>

              <div style={{ border: '1px solid #ccc', padding: '15px', borderRadius: '5px' }}>
                <h3>Button 3: Protected Write Endpoint</h3>
                <p style={{ fontSize: '14px', color: '#666' }}>Requires 'write' or 'admin' scope - should fail for testuser (only has 'read')</p>
                <button 
                  onClick={callWriteEndpoint} 
                  disabled={loading.write}
                  style={{ padding: '10px 20px', fontSize: '16px', marginTop: '10px' }}
                >
                  {loading.write ? 'Loading...' : 'Call Write Endpoint'}
                </button>
                {endpointResults.write && (
                  <pre style={{ marginTop: '10px', fontSize: '12px', overflow: 'auto', backgroundColor: '#f9f9f9', padding: '10px' }}>
                    {JSON.stringify(endpointResults.write, null, 2)}
                  </pre>
                )}
              </div>
            </div>
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
  const [exchanged, setExchanged] = useState(false);
  const [isExchanging, setIsExchanging] = useState(false);

  useEffect(() => {
    // Prevent double execution (e.g. React StrictMode in dev)
    // Use both state flag and localStorage flag for extra safety
    if (exchanged || isExchanging) {
      return;
    }
    
    // Check if we already have a token (code was already exchanged)
    const existingToken = localStorage.getItem('access_token');
    if (existingToken) {
      console.log('Token already exists, redirecting to home');
      setExchanged(true);
      navigate('/');
      return;
    }

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
    
    // Set exchanging flag immediately to prevent double execution
    setIsExchanging(true);
    
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
        const accessToken = response.data.access_token;
        localStorage.setItem('access_token', accessToken);
        if (response.data.refresh_token) {
          localStorage.setItem('refresh_token', response.data.refresh_token);
        }
        localStorage.removeItem('code_verifier');

        // Print token details to console for debugging
        console.log('✅ Token exchange successful!');
        printAccessToken(accessToken);
        
        // Also log the raw response for debugging
        console.log('Token endpoint response:', {
          has_access_token: !!response.data.access_token,
          has_refresh_token: !!response.data.refresh_token,
          scope_in_response: response.data.scope,
          token_type: response.data.token_type,
          expires_in: response.data.expires_in
        });

        // Mark as exchanged to avoid duplicate calls (e.g. StrictMode)
        setExchanged(true);
        setIsExchanging(false);
        
        // Redirect to home
        navigate('/');
      } catch (err: any) {
        // Log full error for debugging
        console.error('Token exchange error:', err?.response?.data || err);
        setError(`Token exchange failed: ${err.response?.data?.error || err.message}`);
        setIsExchanging(false);
      }
    };
    
    exchangeToken();
  }, [searchParams, navigate, exchanged, isExchanging]);

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
