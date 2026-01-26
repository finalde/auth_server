import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { isAuthenticated, initiateLogin } from '../services/auth';

interface AuthGuardProps {
  children: React.ReactNode;
}

export default function AuthGuard({ children }: AuthGuardProps) {
  const navigate = useNavigate();

  useEffect(() => {
    if (!isAuthenticated()) {
      // Not authenticated - initiate login
      initiateLogin();
    }
  }, [navigate]);

  if (!isAuthenticated()) {
    return <div>Redirecting to login...</div>;
  }

  return <>{children}</>;
}
