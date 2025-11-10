import { Routes, Route, Navigate } from 'react-router-dom';
import { useSelector } from 'react-redux';
import Box from '@mui/material/Box';

import Login from './pages/Login';
import TenantLogin from './pages/TenantLogin';
import Register from './pages/Register';
import Dashboard from './pages/Dashboard';
import Repositories from './pages/Repositories';
import AnalysisDetail from './pages/AnalysisDetail';
import Settings from './pages/Settings';
import TenantManagement from './pages/TenantManagement';
import Layout from './components/Layout';

function PrivateRoute({ children }) {
  const isAuthenticated = useSelector((state) => state.auth.isAuthenticated);
  return isAuthenticated ? children : <Navigate to="/login" />;
}

function App() {
  return (
    <Box sx={{ display: 'flex', minHeight: '100vh' }}>
      <Routes>
        {/* Tenant-aware login (NEW - supports multi-tenancy) */}
        <Route path="/tenant-login" element={<TenantLogin />} />
        <Route path="/tenant/:tenantSlug/login" element={<TenantLogin />} />

        {/* Standard login (OLD - backwards compatible) */}
        <Route path="/login" element={<TenantLogin />} />
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
          <Route path="analysis/:id" element={<AnalysisDetail />} />
          <Route path="tenants" element={<TenantManagement />} />
          <Route path="settings" element={<Settings />} />
        </Route>
      </Routes>
    </Box>
  );
}

export default App;
