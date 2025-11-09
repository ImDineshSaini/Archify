import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Container,
  Grid,
  Paper,
  Typography,
  Box,
  Card,
  CardContent,
  CardActions,
  Button,
  Chip,
  CircularProgress,
} from '@mui/material';
import {
  TrendingUp,
  Security,
  Speed,
  BugReport,
} from '@mui/icons-material';
import { analysisAPI, repositoryAPI } from '../services/api';

export default function Dashboard() {
  const [analyses, setAnalyses] = useState([]);
  const [repositories, setRepositories] = useState([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [analysesRes, reposRes] = await Promise.all([
        analysisAPI.list(),
        repositoryAPI.list(),
      ]);
      setAnalyses(analysesRes.data);
      setRepositories(reposRes.data);
    } catch (error) {
      console.error('Error fetching data:', error);
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status) => {
    const colors = {
      completed: 'success',
      running: 'info',
      pending: 'warning',
      failed: 'error',
    };
    return colors[status] || 'default';
  };

  const completedAnalyses = analyses.filter((a) => a.status === 'completed');
  const avgMaintainability =
    completedAnalyses.length > 0
      ? (
          completedAnalyses.reduce((sum, a) => sum + (a.maintainability_score || 0), 0) /
          completedAnalyses.length
        ).toFixed(1)
      : 0;

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Container maxWidth="lg">
      <Typography variant="h4" gutterBottom>
        Dashboard
      </Typography>

      {/* Stats Grid */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Paper sx={{ p: 2, display: 'flex', alignItems: 'center' }}>
            <Box sx={{ flexGrow: 1 }}>
              <Typography color="text.secondary" variant="body2">
                Total Repositories
              </Typography>
              <Typography variant="h4">{repositories.length}</Typography>
            </Box>
            <TrendingUp sx={{ fontSize: 40, color: 'primary.main' }} />
          </Paper>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Paper sx={{ p: 2, display: 'flex', alignItems: 'center' }}>
            <Box sx={{ flexGrow: 1 }}>
              <Typography color="text.secondary" variant="body2">
                Total Analyses
              </Typography>
              <Typography variant="h4">{analyses.length}</Typography>
            </Box>
            <BugReport sx={{ fontSize: 40, color: 'secondary.main' }} />
          </Paper>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Paper sx={{ p: 2, display: 'flex', alignItems: 'center' }}>
            <Box sx={{ flexGrow: 1 }}>
              <Typography color="text.secondary" variant="body2">
                Avg Maintainability
              </Typography>
              <Typography variant="h4">{avgMaintainability}</Typography>
            </Box>
            <Speed sx={{ fontSize: 40, color: 'success.main' }} />
          </Paper>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Paper sx={{ p: 2, display: 'flex', alignItems: 'center' }}>
            <Box sx={{ flexGrow: 1 }}>
              <Typography color="text.secondary" variant="body2">
                Completed
              </Typography>
              <Typography variant="h4">{completedAnalyses.length}</Typography>
            </Box>
            <Security sx={{ fontSize: 40, color: 'warning.main' }} />
          </Paper>
        </Grid>
      </Grid>

      {/* Recent Analyses */}
      <Typography variant="h5" gutterBottom sx={{ mt: 4 }}>
        Recent Analyses
      </Typography>

      {analyses.length === 0 ? (
        <Paper sx={{ p: 4, textAlign: 'center' }}>
          <Typography variant="body1" color="text.secondary">
            No analyses yet. Start by adding a repository!
          </Typography>
          <Button
            variant="contained"
            sx={{ mt: 2 }}
            onClick={() => navigate('/repositories')}
          >
            Add Repository
          </Button>
        </Paper>
      ) : (
        <Grid container spacing={3}>
          {analyses.slice(0, 6).map((analysis) => {
            const repo = repositories.find((r) => r.id === analysis.repository_id);
            return (
              <Grid item xs={12} md={6} key={analysis.id}>
                <Card>
                  <CardContent>
                    <Box display="flex" justifyContent="space-between" alignItems="start">
                      <Box>
                        <Typography variant="h6" gutterBottom>
                          {repo?.name || 'Unknown Repository'}
                        </Typography>
                        <Chip
                          label={analysis.status}
                          color={getStatusColor(analysis.status)}
                          size="small"
                          sx={{ mb: 1 }}
                        />
                      </Box>
                      {analysis.overall_score && (
                        <Chip
                          label={`${analysis.overall_score.toFixed(1)}/100`}
                          color="primary"
                          variant="outlined"
                        />
                      )}
                    </Box>

                    {analysis.status === 'completed' && (
                      <Box sx={{ mt: 2 }}>
                        <Typography variant="body2" color="text.secondary">
                          Maintainability: {analysis.maintainability_score?.toFixed(1) || 'N/A'}
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          Reliability: {analysis.reliability_score?.toFixed(1) || 'N/A'}
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          Scalability: {analysis.scalability_score?.toFixed(1) || 'N/A'}
                        </Typography>
                      </Box>
                    )}
                  </CardContent>
                  <CardActions>
                    <Button size="small" onClick={() => navigate(`/analysis/${analysis.id}`)}>
                      View Details
                    </Button>
                  </CardActions>
                </Card>
              </Grid>
            );
          })}
        </Grid>
      )}
    </Container>
  );
}
