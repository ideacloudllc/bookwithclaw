import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ProtectedRoute } from './components/ProtectedRoute';
import { Signup } from './pages/Signup';
import { Login } from './pages/Login';
import { Dashboard } from './pages/Dashboard';
import { getAuthToken } from './utils/auth';

function App() {
  const isAuthenticated = !!getAuthToken();

  return (
    <Router basename="/sellers">
      <Routes>
        {/* If logged in, redirect away from signup/login */}
        <Route 
          path="/" 
          element={isAuthenticated ? <Navigate to="/portal" replace /> : <Signup />} 
        />
        <Route 
          path="/login" 
          element={isAuthenticated ? <Navigate to="/portal" replace /> : <Login />} 
        />
        {/* Protected dashboard with nested routes */}
        <Route
          path="/portal/*"
          element={
            <ProtectedRoute>
              <Dashboard />
            </ProtectedRoute>
          }
        />
        <Route path="*" element={<Navigate to={isAuthenticated ? "/portal" : "/"} replace />} />
      </Routes>
    </Router>
  );
}

export default App;
