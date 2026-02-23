import { Routes, Route, Navigate } from 'react-router-dom';
import { useSelector } from 'react-redux';
import Box from '@mui/material/Box';

import Login from './pages/Login';
import TenantLogin from './pages/TenantLogin';
import Register from './pages/Register';
import Dashboard from './pages/Dashboard';
import Repositories from './pages/Repositories';
import AnalysisDetailEnhanced from './pages/AnalysisDetailEnhanced';
import AnalysisHistory from './pages/AnalysisHistory';
import Settings from './pages/Settings';
import TenantManagement from './pages/TenantManagement';
import Layout from './components/Layout';

function PrivateRoute({ children }) {
  const isAuthenticated = useSelector((state) => state.auth.isAuthenticated);
  return isAuthenticated ? children : <Navigate to="/login" />;
}

function AdminRoute({ children }) {
  const isAdmin = useSelector((state) => state.auth.isAdmin);
  return isAdmin ? children : <Navigate to="/" />;
}

function App() {
  return (
    <Box sx={{ display: 'flex', minHeight: '100vh' }}>
      <Routes>
        {/* Tenant-aware login (NEW - supports multi-tenancy) */}
        <Route path="/tenant-login" element={<TenantLogin />} />
        <Route path="/tenant/:tenantSlug/login" element={<TenantLogin />} />

        {/* Standard login */}
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />

        <Route
          path="/"
          element={
            <PrivateRoute>
              <Layout />
            </PrivateRoute>
          }
        >
          <Route index element={<Dashboard />} />
          <Route path="repositories" element={<Repositories />} />
          <Route path="analysis/:id" element={<AnalysisDetailEnhanced />} />
          <Route path="analysis-history" element={<AnalysisHistory />} />
          <Route path="tenants" element={<AdminRoute><TenantManagement /></AdminRoute>} />
          <Route path="settings" element={<AdminRoute><Settings /></AdminRoute>} />
        </Route>
      </Routes>
    </Box>
  );
}

export default App;
