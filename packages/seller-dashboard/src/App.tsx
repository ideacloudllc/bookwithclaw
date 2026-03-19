import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ProtectedRoute } from './components/ProtectedRoute';
import { Signup } from './pages/Signup';
import { Login } from './pages/Login';
import { Dashboard } from './pages/Dashboard';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/sellers" element={<Signup />} />
        <Route path="/sellers/login" element={<Login />} />
        <Route
          path="/sellers/portal"
          element={
            <ProtectedRoute>
              <Dashboard />
            </ProtectedRoute>
          }
        />
        <Route path="/" element={<Navigate to="/sellers" replace />} />
        <Route path="*" element={<Navigate to="/sellers" replace />} />
      </Routes>
    </Router>
  );
}

export default App;
