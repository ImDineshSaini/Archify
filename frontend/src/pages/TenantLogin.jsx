import { useState } from 'react';
import { useNavigate, Link, useParams, useSearchParams } from 'react-router-dom';
import { useDispatch } from 'react-redux';
import {
  Container,
  Box,
  Paper,
  Typography,
  TextField,
  Button,
  Alert,
  Link as MuiLink,
  Divider,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Chip,
} from '@mui/material';
import { Business, Login as LoginIcon } from '@mui/icons-material';
import { loginStart, loginSuccess, loginFailure } from '../store/authSlice';
import axios from 'axios';

export default function TenantLogin() {
  const { tenantSlug } = useParams(); // For URL like /tenant/acme/login
  const [searchParams] = useSearchParams();
  const urlTenant = searchParams.get('tenant'); // For URL like /login?tenant=acme

  const [formData, setFormData] = useState({
    username: '',
    password: '',
    tenant: tenantSlug || urlTenant || '',
  });
  const [error, setError] = useState('');
  const [showTenantInput, setShowTenantInput] = useState(!tenantSlug && !urlTenant);
  const navigate = useNavigate();
  const dispatch = useDispatch();

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    dispatch(loginStart());

    try {
      // Use v2 auth endpoint which supports tenant login
      const response = await axios.post('/api/v2/auth/login', {
        username: formData.username,
        password: formData.password,
      }, {
        headers: formData.tenant ? { 'X-Tenant-Slug': formData.tenant } : {},
      });

      const { access_token, user_id, username } = response.data;

      // Store auth data
      localStorage.setItem('token', access_token);
      localStorage.setItem('tenant', formData.tenant || '');

      dispatch(loginSuccess({
        token: access_token,
        user: {
          id: user_id,
          username: username,
          tenant: formData.tenant,
        }
      }));

      navigate('/');
    } catch (err) {
      const message = err.response?.data?.error?.message ||
                     err.response?.data?.detail ||
                     'Login failed';
      setError(message);
      dispatch(loginFailure(message));
    }
  };

  const handleSwitchToStandard = () => {
    setShowTenantInput(false);
    setFormData({ ...formData, tenant: '' });
  };

  const handleSwitchToTenant = () => {
    setShowTenantInput(true);
  };

  return (
    <Container component="main" maxWidth="xs">
      <Box
        sx={{
          marginTop: 8,
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
        }}
      >
        <Paper elevation={3} sx={{ p: 4, width: '100%' }}>
          {/* Header */}
          <Typography component="h1" variant="h4" align="center" gutterBottom>
            Archify
          </Typography>
          <Typography component="h2" variant="h6" align="center" color="text.secondary" gutterBottom>
            {formData.tenant ? (
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 1 }}>
                <Business fontSize="small" />
                <span>Sign in to</span>
                <Chip label={formData.tenant} size="small" color="primary" />
              </Box>
            ) : (
              'Sign in'
            )}
          </Typography>

          {error && (
            <Alert severity="error" sx={{ mt: 2 }}>
              {error}
            </Alert>
          )}

          <Box component="form" onSubmit={handleSubmit} sx={{ mt: 3 }}>
            {/* Tenant Selection - Only show if not in URL */}
            {showTenantInput && (
              <TextField
                margin="normal"
                fullWidth
                id="tenant"
                label="Organization/Tenant (optional)"
                name="tenant"
                placeholder="acme"
                value={formData.tenant}
                onChange={handleChange}
                helperText="Leave empty for single-tenant mode"
                InputProps={{
                  startAdornment: <Business sx={{ mr: 1, color: 'action.active' }} />,
                }}
              />
            )}

            {/* Tenant slug from URL - show as read-only chip */}
            {tenantSlug && (
              <Alert severity="info" sx={{ mt: 2, mb: 1 }}>
                Logging into: <strong>{tenantSlug}</strong>
              </Alert>
            )}

            <TextField
              margin="normal"
              required
              fullWidth
              id="username"
              label="Username"
              name="username"
              autoComplete="username"
              autoFocus={!showTenantInput}
              value={formData.username}
              onChange={handleChange}
            />

            <TextField
              margin="normal"
              required
              fullWidth
              name="password"
              label="Password"
              type="password"
              id="password"
              autoComplete="current-password"
              value={formData.password}
              onChange={handleChange}
            />

            <Button
              type="submit"
              fullWidth
              variant="contained"
              sx={{ mt: 3, mb: 2 }}
              startIcon={<LoginIcon />}
            >
              Sign In
            </Button>

            {/* Toggle between tenant and standard login */}
            {!tenantSlug && !urlTenant && (
              <>
                <Divider sx={{ my: 2 }}>
                  <Typography variant="caption" color="text.secondary">
                    OR
                  </Typography>
                </Divider>

                {showTenantInput ? (
                  <Button
                    fullWidth
                    variant="outlined"
                    size="small"
                    onClick={handleSwitchToStandard}
                  >
                    Sign in without tenant
                  </Button>
                ) : (
                  <Button
                    fullWidth
                    variant="outlined"
                    size="small"
                    onClick={handleSwitchToTenant}
                    startIcon={<Business />}
                  >
                    Sign in to organization
                  </Button>
                )}
              </>
            )}

            <Box sx={{ textAlign: 'center', mt: 2 }}>
              <MuiLink component={Link} to="/register" variant="body2">
                Don't have an account? Sign Up
              </MuiLink>
            </Box>
          </Box>
        </Paper>

        {/* Info about multi-tenancy */}
        {showTenantInput && (
          <Alert severity="info" sx={{ mt: 2, width: '100%' }}>
            <Typography variant="caption">
              <strong>Multi-Tenant Login:</strong><br />
              If your organization uses Archify, enter your organization's slug to access your isolated workspace.
              Ask your administrator if you're unsure.
            </Typography>
          </Alert>
        )}
      </Box>
    </Container>
  );
}
