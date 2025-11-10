import { useState, useEffect } from 'react';
import {
  Container,
  Typography,
  Box,
  Paper,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Chip,
  IconButton,
  Alert,
} from '@mui/material';
import { Add, Delete, Edit } from '@mui/icons-material';
import { tenantAPI } from '../services/tenant-api';

export default function TenantManagement() {
  const [tenants, setTenants] = useState([]);
  const [openDialog, setOpenDialog] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    slug: '',
    admin_email: '',
    admin_name: '',
    admin_password: '',
  });
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchTenants();
  }, []);

  const fetchTenants = async () => {
    try {
      const response = await tenantAPI.list();
      setTenants(response.data);
    } catch (error) {
      console.error('Error fetching tenants:', error);
    }
  };

  const handleOpenDialog = () => {
    setOpenDialog(true);
    setError('');
    setSuccess('');
  };

  const handleCloseDialog = () => {
    setOpenDialog(false);
    setFormData({
      name: '',
      slug: '',
      admin_email: '',
      admin_name: '',
      admin_password: '',
    });
    setError('');
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({ ...formData, [name]: value });

    // Auto-generate slug from name
    if (name === 'name') {
      const slug = value
        .toLowerCase()
        .replace(/[^a-z0-9]+/g, '-')
        .replace(/^-+|-+$/g, '');
      setFormData((prev) => ({ ...prev, slug }));
    }
  };

  const handleSubmit = async () => {
    setError('');
    setSuccess('');
    setLoading(true);

    try {
      await tenantAPI.create(formData);
      setSuccess('Tenant created successfully! Schema has been provisioned.');
      await fetchTenants();
      setTimeout(() => {
        handleCloseDialog();
      }, 2000);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to create tenant');
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id, name) => {
    if (
      window.confirm(
        `Are you sure you want to delete tenant "${name}"? This will permanently delete all data!`
      )
    ) {
      try {
        await tenantAPI.delete(id);
        setSuccess('Tenant deleted successfully');
        await fetchTenants();
      } catch (error) {
        setError('Failed to delete tenant');
        console.error('Error deleting tenant:', error);
      }
    }
  };

  const handleToggleStatus = async (tenant) => {
    try {
      await tenantAPI.update(tenant.id, { is_active: !tenant.is_active });
      await fetchTenants();
    } catch (error) {
      console.error('Error updating tenant:', error);
    }
  };

  return (
    <Container maxWidth="lg">
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4">Tenant Management</Typography>
        <Button variant="contained" startIcon={<Add />} onClick={handleOpenDialog}>
          Create Tenant
        </Button>
      </Box>

      {success && <Alert severity="success" sx={{ mb: 2 }}>{success}</Alert>}
      {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}

      <Alert severity="info" sx={{ mb: 3 }}>
        Each tenant gets an isolated PostgreSQL schema with automatic setup and admin user creation.
      </Alert>

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Organization</TableCell>
              <TableCell>Slug</TableCell>
              <TableCell>Schema</TableCell>
              <TableCell>Admin Email</TableCell>
              <TableCell>Status</TableCell>
              <TableCell>Type</TableCell>
              <TableCell>Created</TableCell>
              <TableCell>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {tenants.length === 0 ? (
              <TableRow>
                <TableCell colSpan={8} align="center">
                  <Typography variant="body2" color="text.secondary">
                    No tenants yet. Create your first tenant to get started.
                  </Typography>
                </TableCell>
              </TableRow>
            ) : (
              tenants.map((tenant) => (
                <TableRow key={tenant.id}>
                  <TableCell>{tenant.name}</TableCell>
                  <TableCell>
                    <Chip label={tenant.slug} size="small" />
                  </TableCell>
                  <TableCell>
                    <code>{tenant.schema_name}</code>
                  </TableCell>
                  <TableCell>{tenant.admin_email}</TableCell>
                  <TableCell>
                    <Chip
                      label={tenant.is_active ? 'Active' : 'Inactive'}
                      color={tenant.is_active ? 'success' : 'default'}
                      size="small"
                      onClick={() => handleToggleStatus(tenant)}
                      sx={{ cursor: 'pointer' }}
                    />
                  </TableCell>
                  <TableCell>
                    <Chip
                      label={tenant.is_trial ? 'Trial' : 'Paid'}
                      color={tenant.is_trial ? 'warning' : 'primary'}
                      size="small"
                    />
                  </TableCell>
                  <TableCell>
                    {new Date(tenant.created_at).toLocaleDateString()}
                  </TableCell>
                  <TableCell>
                    <IconButton
                      size="small"
                      color="error"
                      onClick={() => handleDelete(tenant.id, tenant.name)}
                    >
                      <Delete />
                    </IconButton>
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </TableContainer>

      {/* Create Tenant Dialog */}
      <Dialog open={openDialog} onClose={handleCloseDialog} maxWidth="sm" fullWidth>
        <DialogTitle>Create New Tenant</DialogTitle>
        <DialogContent>
          {error && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {error}
            </Alert>
          )}
          {success && (
            <Alert severity="success" sx={{ mb: 2 }}>
              {success}
            </Alert>
          )}

          <TextField
            margin="normal"
            fullWidth
            label="Organization Name"
            name="name"
            value={formData.name}
            onChange={handleChange}
            required
            autoFocus
          />

          <TextField
            margin="normal"
            fullWidth
            label="Slug"
            name="slug"
            value={formData.slug}
            onChange={handleChange}
            helperText="URL-safe identifier (auto-generated from name)"
            required
          />

          <TextField
            margin="normal"
            fullWidth
            label="Admin Email"
            name="admin_email"
            type="email"
            value={formData.admin_email}
            onChange={handleChange}
            required
          />

          <TextField
            margin="normal"
            fullWidth
            label="Admin Name"
            name="admin_name"
            value={formData.admin_name}
            onChange={handleChange}
          />

          <TextField
            margin="normal"
            fullWidth
            label="Admin Password"
            name="admin_password"
            type="password"
            value={formData.admin_password}
            onChange={handleChange}
            helperText="Password for the tenant's admin user"
            required
          />

          <Alert severity="info" sx={{ mt: 2 }}>
            This will create:
            <ul>
              <li>A new PostgreSQL schema: tenant_{'{'}slug{'}'}</li>
              <li>All necessary database tables</li>
              <li>An admin user for the tenant</li>
            </ul>
          </Alert>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog}>Cancel</Button>
          <Button
            onClick={handleSubmit}
            variant="contained"
            disabled={
              loading ||
              !formData.name ||
              !formData.slug ||
              !formData.admin_email ||
              !formData.admin_password
            }
          >
            {loading ? 'Creating...' : 'Create Tenant'}
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
}
