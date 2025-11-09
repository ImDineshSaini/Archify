import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Container,
  Typography,
  Box,
  Paper,
  Grid,
  Card,
  CardContent,
  Chip,
  CircularProgress,
  LinearProgress,
  Button,
  Divider,
  List,
  ListItem,
  ListItemText,
  Alert,
} from '@mui/material';
import { ArrowBack, Refresh } from '@mui/icons-material';
import { RadialBarChart, RadialBar, Legend, ResponsiveContainer } from 'recharts';
import { analysisAPI, repositoryAPI } from '../services/api';

export default function AnalysisDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [analysis, setAnalysis] = useState(null);
  const [repository, setRepository] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchAnalysis();
    const interval = setInterval(() => {
      fetchAnalysis(true);
    }, 5000);
    return () => clearInterval(interval);
  }, [id]);

  const fetchAnalysis = async (silent = false) => {
    try {
      if (!silent) setLoading(true);
      const response = await analysisAPI.get(id);
      setAnalysis(response.data);

      if (response.data.repository_id) {
        const repoResponse = await repositoryAPI.get(response.data.repository_id);
        setRepository(repoResponse.data);
      }
    } catch (error) {
      console.error('Error fetching analysis:', error);
    } finally {
      if (!silent) setLoading(false);
    }
  };

  if (loading || !analysis) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  const getStatusColor = (status) => {
    const colors = {
      completed: 'success',
      running: 'info',
      pending: 'warning',
      failed: 'error',
    };
    return colors[status] || 'default';
  };

  const getScoreColor = (score) => {
    if (score >= 80) return 'success';
    if (score >= 60) return 'warning';
    return 'error';
  };

  const chartData = analysis.status === 'completed' ? [
    {
      name: 'Maintainability',
      value: analysis.maintainability_score || 0,
      fill: '#8884d8',
    },
    {
      name: 'Reliability',
      value: analysis.reliability_score || 0,
      fill: '#83a6ed',
    },
    {
      name: 'Scalability',
      value: analysis.scalability_score || 0,
      fill: '#8dd1e1',
    },
    {
      name: 'Security',
      value: analysis.security_score || 0,
      fill: '#82ca9d',
    },
  ] : [];

  return (
    <Container maxWidth="lg">
      <Box display="flex" alignItems="center" mb={3}>
        <Button startIcon={<ArrowBack />} onClick={() => navigate(-1)} sx={{ mr: 2 }}>
          Back
        </Button>
        <Typography variant="h4" sx={{ flexGrow: 1 }}>
          Analysis Results
        </Typography>
        <Button startIcon={<Refresh />} onClick={() => fetchAnalysis()}>
          Refresh
        </Button>
      </Box>

      {/* Repository Info */}
      {repository && (
        <Paper sx={{ p: 3, mb: 3 }}>
          <Typography variant="h6" gutterBottom>
            {repository.name}
          </Typography>
          <Typography variant="body2" color="text.secondary">
            {repository.description || 'No description'}
          </Typography>
          <Box mt={1}>
            <Chip label={repository.source} size="small" />
            {repository.language && (
              <Chip label={repository.language} size="small" sx={{ ml: 1 }} />
            )}
          </Box>
        </Paper>
      )}

      {/* Status */}
      <Paper sx={{ p: 3, mb: 3 }}>
        <Box display="flex" alignItems="center" justifyContent="space-between">
          <Typography variant="h6">Status</Typography>
          <Chip label={analysis.status} color={getStatusColor(analysis.status)} />
        </Box>

        {analysis.status === 'running' && (
          <Box mt={2}>
            <LinearProgress />
            <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
              Analysis in progress...
            </Typography>
          </Box>
        )}

        {analysis.status === 'failed' && (
          <Alert severity="error" sx={{ mt: 2 }}>
            {analysis.error_message || 'Analysis failed'}
          </Alert>
        )}
      </Paper>

      {analysis.status === 'completed' && (
        <>
          {/* Overall Score */}
          <Paper sx={{ p: 3, mb: 3, textAlign: 'center' }}>
            <Typography variant="h6" gutterBottom>
              Overall Quality Score
            </Typography>
            <Typography variant="h2" color={`${getScoreColor(analysis.overall_score)}.main`}>
              {analysis.overall_score?.toFixed(1)}/100
            </Typography>
          </Paper>

          {/* Score Breakdown */}
          <Grid container spacing={3} sx={{ mb: 3 }}>
            <Grid item xs={12} md={6}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Maintainability
                  </Typography>
                  <Box display="flex" alignItems="center">
                    <Typography variant="h4" color={`${getScoreColor(analysis.maintainability_score)}.main`}>
                      {analysis.maintainability_score?.toFixed(1)}
                    </Typography>
                    <Typography variant="h6" color="text.secondary" sx={{ ml: 1 }}>
                      /100
                    </Typography>
                  </Box>
                  <LinearProgress
                    variant="determinate"
                    value={analysis.maintainability_score}
                    color={getScoreColor(analysis.maintainability_score)}
                    sx={{ mt: 2 }}
                  />
                </CardContent>
              </Card>
            </Grid>

            <Grid item xs={12} md={6}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Reliability
                  </Typography>
                  <Box display="flex" alignItems="center">
                    <Typography variant="h4" color={`${getScoreColor(analysis.reliability_score)}.main`}>
                      {analysis.reliability_score?.toFixed(1)}
                    </Typography>
                    <Typography variant="h6" color="text.secondary" sx={{ ml: 1 }}>
                      /100
                    </Typography>
                  </Box>
                  <LinearProgress
                    variant="determinate"
                    value={analysis.reliability_score}
                    color={getScoreColor(analysis.reliability_score)}
                    sx={{ mt: 2 }}
                  />
                </CardContent>
              </Card>
            </Grid>

            <Grid item xs={12} md={6}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Scalability
                  </Typography>
                  <Box display="flex" alignItems="center">
                    <Typography variant="h4" color={`${getScoreColor(analysis.scalability_score)}.main`}>
                      {analysis.scalability_score?.toFixed(1)}
                    </Typography>
                    <Typography variant="h6" color="text.secondary" sx={{ ml: 1 }}>
                      /100
                    </Typography>
                  </Box>
                  <LinearProgress
                    variant="determinate"
                    value={analysis.scalability_score}
                    color={getScoreColor(analysis.scalability_score)}
                    sx={{ mt: 2 }}
                  />
                </CardContent>
              </Card>
            </Grid>

            <Grid item xs={12} md={6}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Security
                  </Typography>
                  <Box display="flex" alignItems="center">
                    <Typography variant="h4" color={`${getScoreColor(analysis.security_score)}.main`}>
                      {analysis.security_score?.toFixed(1)}
                    </Typography>
                    <Typography variant="h6" color="text.secondary" sx={{ ml: 1 }}>
                      /100
                    </Typography>
                  </Box>
                  <LinearProgress
                    variant="determinate"
                    value={analysis.security_score}
                    color={getScoreColor(analysis.security_score)}
                    sx={{ mt: 2 }}
                  />
                </CardContent>
              </Card>
            </Grid>
          </Grid>

          {/* Code Metrics */}
          {analysis.code_metrics && (
            <Paper sx={{ p: 3, mb: 3 }}>
              <Typography variant="h6" gutterBottom>
                Code Metrics
              </Typography>
              <Grid container spacing={2}>
                <Grid item xs={6} md={3}>
                  <Typography variant="body2" color="text.secondary">
                    Total Lines
                  </Typography>
                  <Typography variant="h6">
                    {analysis.code_metrics.total_lines?.toLocaleString()}
                  </Typography>
                </Grid>
                <Grid item xs={6} md={3}>
                  <Typography variant="body2" color="text.secondary">
                    Files Analyzed
                  </Typography>
                  <Typography variant="h6">
                    {analysis.code_metrics.files_analyzed}
                  </Typography>
                </Grid>
                <Grid item xs={6} md={3}>
                  <Typography variant="body2" color="text.secondary">
                    Code Lines
                  </Typography>
                  <Typography variant="h6">
                    {analysis.code_metrics.code_lines?.toLocaleString()}
                  </Typography>
                </Grid>
                <Grid item xs={6} md={3}>
                  <Typography variant="body2" color="text.secondary">
                    Comment Lines
                  </Typography>
                  <Typography variant="h6">
                    {analysis.code_metrics.comment_lines?.toLocaleString()}
                  </Typography>
                </Grid>
              </Grid>
            </Paper>
          )}

          {/* AI Suggestions */}
          {analysis.suggestions && (
            <Paper sx={{ p: 3, mb: 3 }}>
              <Typography variant="h6" gutterBottom>
                AI-Powered Suggestions
              </Typography>
              <Divider sx={{ mb: 2 }} />
              <Typography variant="body1" sx={{ whiteSpace: 'pre-wrap' }}>
                {analysis.suggestions}
              </Typography>
            </Paper>
          )}

          {/* Issues */}
          {analysis.issues && analysis.issues.length > 0 && (
            <Paper sx={{ p: 3 }}>
              <Typography variant="h6" gutterBottom>
                Issues Found ({analysis.issues.length})
              </Typography>
              <List>
                {analysis.issues.slice(0, 10).map((issue, index) => (
                  <ListItem key={index} divider>
                    <ListItemText
                      primary={issue.message}
                      secondary={`Type: ${issue.type} | Severity: ${issue.severity}`}
                    />
                  </ListItem>
                ))}
              </List>
            </Paper>
          )}
        </>
      )}
    </Container>
  );
}
