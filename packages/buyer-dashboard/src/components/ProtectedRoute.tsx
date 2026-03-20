import { Navigate } from 'react-router-dom';
import { getAuthToken } from '../utils/auth';

interface ProtectedRouteProps {
  children: React.ReactNode;
}

export const ProtectedRoute = ({ children }: ProtectedRouteProps) => {
  const token = getAuthToken();
  
  if (!token) {
    return <Navigate to="/buyers/login" replace />;
  }

  return <>{children}</>;
};
