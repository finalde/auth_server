import { BrowserRouter, Routes, Route, Navigate, useSearchParams } from 'react-router-dom';
import { useEffect, useState } from 'react';
import Layout from './components/Layout';
import ClientsPage from './pages/ClientsPage';
import UsersPage from './pages/UsersPage';
import ResourcesPage from './pages/ResourcesPage';
import ScopesPage from './pages/ScopesPage';
import UserClaimsPage from './pages/UserClaimsPage';
import UserScopesPage from './pages/UserScopesPage';
import DashboardPage from './pages/DashboardPage';
import AuthGuard from './components/AuthGuard';
import { exchangeCodeForToken, isAuthenticated } from './services/auth';

function Callback() {
  const [searchParams] = useSearchParams();
  const [error, setError] = useState<string | null>(null);
  const [exchanged, setExchanged] = useState(false);

  useEffect(() => {
    if (exchanged) return;
    
    // Check if we already have a token
    if (isAuthenticated()) {
      setExchanged(true);
      window.location.href = '/';
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
    
    exchangeCodeForToken(code)
      .then(() => {
        setExchanged(true);
        window.location.href = '/';
      })
      .catch((err) => {
        setError(`Token exchange error: ${err.message}`);
      });
  }, [searchParams, exchanged]);

  if (error) {
    return (
      <div style={{ padding: '20px' }}>
        <h2>Authentication Error</h2>
        <p>{error}</p>
        <button onClick={() => window.location.href = '/'}>Go to Home</button>
      </div>
    );
  }

  return <div style={{ padding: '20px' }}>Completing authentication...</div>;
}

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/callback" element={<Callback />} />
        <Route
          path="/*"
          element={
            <AuthGuard>
              <Layout>
                <Routes>
                  <Route path="/" element={<Navigate to="/dashboard" replace />} />
                  <Route path="/dashboard" element={<DashboardPage />} />
                  <Route path="/clients" element={<ClientsPage />} />
                  <Route path="/users" element={<UsersPage />} />
                  <Route path="/resources" element={<ResourcesPage />} />
                  <Route path="/scopes" element={<ScopesPage />} />
                  <Route path="/user-claims" element={<UserClaimsPage />} />
                  <Route path="/user-scopes" element={<UserScopesPage />} />
                </Routes>
              </Layout>
            </AuthGuard>
          }
        />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
