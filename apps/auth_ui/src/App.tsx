import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import Layout from './components/Layout';
import ClientsPage from './pages/ClientsPage';
import UsersPage from './pages/UsersPage';
import ResourcesPage from './pages/ResourcesPage';
import ScopesPage from './pages/ScopesPage';
import DashboardPage from './pages/DashboardPage';

function App() {
  return (
    <BrowserRouter>
      <Layout>
        <Routes>
          <Route path="/" element={<Navigate to="/dashboard" replace />} />
          <Route path="/dashboard" element={<DashboardPage />} />
          <Route path="/clients" element={<ClientsPage />} />
          <Route path="/users" element={<UsersPage />} />
          <Route path="/resources" element={<ResourcesPage />} />
          <Route path="/scopes" element={<ScopesPage />} />
        </Routes>
      </Layout>
    </BrowserRouter>
  );
}

export default App;
