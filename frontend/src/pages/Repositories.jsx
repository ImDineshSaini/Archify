import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Container,
  Typography,
  Button,
  Box,
  Card,
  CardContent,
  CardActions,
  Grid,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Alert,
  Chip,
  IconButton,
  CircularProgress,
} from '@mui/material';
import { Add, Delete, PlayArrow, Folder, Refresh, Star, CallSplit } from '@mui/icons-material';
import { repositoryAPI, analysisAPI } from '../services/api';

export default function Repositories() {
  const [repositories, setRepositories] = useState([]);
  const [openDialog, setOpenDialog] = useState(false);
  const [formData, setFormData] = useState({
    url: '',
    source: 'github',
    access_token: '',
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [analyzingRepoId, setAnalyzingRepoId] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    fetchRepositories();
  }, []);

  const fetchRepositories = async () => {
    try {
      const response = await repositoryAPI.list();
      setRepositories(response.data);
    } catch (error) {
      console.error('Error fetching repositories:', error);
    }
  };

  const handleOpenDialog = () => {
    setOpenDialog(true);
    setError('');
  };

  const handleCloseDialog = () => {
    setOpenDialog(false);
    setFormData({ url: '', source: 'github', access_token: '' });
    setError('');
  };

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async () => {
    setError('');
    setLoading(true);

    try {
      const submitData = { ...formData };
      if (!submitData.access_token) {
        delete submitData.access_token;
      }

      await repositoryAPI.create(submitData);
      await fetchRepositories();
      handleCloseDialog();
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to add repository');
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id) => {
    if (window.confirm('Are you sure you want to delete this repository?')) {
      try {
        await repositoryAPI.delete(id);
        await fetchRepositories();
      } catch (error) {
        console.error('Error deleting repository:', error);
      }
    }
  };

  const handleStartAnalysis = async (repositoryId) => {
    try {
      setAnalyzingRepoId(repositoryId);
      const response = await analysisAPI.create({ repository_id: repositoryId });
      // Navigate to analysis page immediately to show progress
      navigate(`/analysis/${response.data.id}`);
    } catch (error) {
      console.error('Error starting analysis:', error);
      alert('Failed to start analysis: ' + (error.response?.data?.detail || error.message));
      setAnalyzingRepoId(null);
    }
  };

  return (
    <Container maxWidth="lg">
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4">Repositories</Typography>
        <Button
          variant="contained"
          startIcon={<Add />}
          onClick={handleOpenDialog}
        >
          Add Repository
        </Button>
      </Box>

      {repositories.length === 0 ? (
        <Card sx={{ p: 4, textAlign: 'center' }}>
          <Folder sx={{ fontSize: 80, color: 'text.secondary', mb: 2 }} />
          <Typography variant="h6" gutterBottom>
            No repositories yet
          </Typography>
          <Typography variant="body2" color="text.secondary" paragraph>
            Add a repository to start analyzing your code
          </Typography>
          <Button variant="contained" onClick={handleOpenDialog}>
            Add Your First Repository
          </Button>
        </Card>
      ) : (
        <Grid container spacing={3}>
          {repositories.map((repo) => (
            <Grid item xs={12} md={6} key={repo.id}>
              <Card>
                <CardContent>
                  <Box display="flex" justifyContent="space-between" alignItems="start">
                    <Box>
                      <Typography variant="h6" gutterBottom>
                        {repo.name}
                      </Typography>
                      <Chip label={repo.source} size="small" sx={{ mb: 1 }} />
                      {repo.language && (
                        <Chip
                          label={repo.language}
                          size="small"
                          variant="outlined"
                          sx={{ ml: 1, mb: 1 }}
                        />
                      )}
                    </Box>
                    <IconButton
                      size="small"
                      color="error"
                      onClick={() => handleDelete(repo.id)}
                    >
                      <Delete />
                    </IconButton>
                  </Box>

                  <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                    {repo.description || 'No description'}
                  </Typography>

                  <Box display="flex" gap={2}>
                    <Typography variant="caption" color="text.secondary" sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                      <Star sx={{ fontSize: 14 }} /> {repo.stars}
                    </Typography>
                    <Typography variant="caption" color="text.secondary" sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
                      <CallSplit sx={{ fontSize: 14 }} /> {repo.forks}
                    </Typography>
                  </Box>
                </CardContent>
                <CardActions>
                  <Button
                    size="small"
                    variant={analyzingRepoId === repo.id ? "contained" : "outlined"}
                    startIcon={analyzingRepoId === repo.id ? <CircularProgress size={16} /> : <PlayArrow />}
                    onClick={() => handleStartAnalysis(repo.id)}
                    disabled={analyzingRepoId === repo.id}
                  >
                    {analyzingRepoId === repo.id ? 'Starting Analysis...' : 'Start Analysis'}
                  </Button>
                  <Button
                    size="small"
                    href={repo.url}
                    target="_blank"
                    rel="noopener noreferrer"
                  >
                    View on {repo.source}
                  </Button>
                </CardActions>
              </Card>
            </Grid>
          ))}
        </Grid>
      )}

      {/* Add Repository Dialog */}
      <Dialog open={openDialog} onClose={handleCloseDialog} maxWidth="sm" fullWidth>
        <DialogTitle>Add Repository</DialogTitle>
        <DialogContent>
          {error && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {error}
            </Alert>
          )}

          <FormControl fullWidth sx={{ mt: 2 }}>
            <InputLabel>Source</InputLabel>
            <Select
              name="source"
              value={formData.source}
              label="Source"
              onChange={handleChange}
            >
              <MenuItem value="github">GitHub</MenuItem>
              <MenuItem value="gitlab">GitLab</MenuItem>
            </Select>
          </FormControl>

          <TextField
            margin="normal"
            fullWidth
            label="Repository URL"
            name="url"
            placeholder="https://github.com/username/repository"
            value={formData.url}
            onChange={handleChange}
            required
          />

          <TextField
            margin="normal"
            fullWidth
            label="Access Token (Optional)"
            name="access_token"
            type="password"
            helperText="Required for private repositories"
            value={formData.access_token}
            onChange={handleChange}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog}>Cancel</Button>
          <Button
            onClick={handleSubmit}
            variant="contained"
            disabled={loading || !formData.url}
          >
            {loading ? 'Adding...' : 'Add Repository'}
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
}
