import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
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
} from '@mui/material';
import { loginStart, loginSuccess, loginFailure } from '../store/authSlice';
import { authAPI } from '../services/api';

export default function Login() {
  const [formData, setFormData] = useState({ username: '', password: '' });
  const [error, setError] = useState('');
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
      const response = await authAPI.login(formData);
      dispatch(loginSuccess({
        token: response.data.access_token,
        user: { username: formData.username }
      }));
      navigate('/');
    } catch (err) {
      const message = err.response?.data?.detail || 'Login failed';
      setError(message);
      dispatch(loginFailure(message));
    }
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
          <Typography component="h1" variant="h4" align="center" gutterBottom>
            Archify
          </Typography>
          <Typography component="h2" variant="h6" align="center" color="text.secondary" gutterBottom>
            Sign in
          </Typography>

          {error && (
            <Alert severity="error" sx={{ mt: 2 }}>
              {error}
            </Alert>
          )}

          <Box component="form" onSubmit={handleSubmit} sx={{ mt: 3 }}>
            <TextField
              margin="normal"
              required
              fullWidth
              id="username"
              label="Username"
              name="username"
              autoComplete="username"
              autoFocus
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
            >
              Sign In
            </Button>
            <Box sx={{ textAlign: 'center' }}>
              <MuiLink component={Link} to="/register" variant="body2">
                Don't have an account? Sign Up
              </MuiLink>
            </Box>
          </Box>
        </Paper>
      </Box>
    </Container>
  );
}
