import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Container,
  Typography,
  Box,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TablePagination,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Chip,
  IconButton,
  Button,
  Grid,
  Card,
  CardContent,
  Tooltip,
  Menu,
  ListItemIcon,
  ListItemText,
} from '@mui/material';
import {
  Visibility,
  Refresh as RefreshIcon,
  Delete,
  MoreVert,
  FilterList,
  TrendingUp,
  CheckCircle,
  Error,
  HourglassEmpty,
  Assessment,
} from '@mui/icons-material';
import { analysisAPI, repositoryAPI } from '../services/api';

export default function AnalysisHistory() {
  const navigate = useNavigate();
  const [analyses, setAnalyses] = useState([]);
  const [repositories, setRepositories] = useState({});
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const [filterStatus, setFilterStatus] = useState('all');
  const [filterRepo, setFilterRepo] = useState('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [anchorEl, setAnchorEl] = useState(null);
  const [selectedAnalysis, setSelectedAnalysis] = useState(null);

  // Statistics
  const [stats, setStats] = useState({
    total: 0,
    completed: 0,
    running: 0,
    failed: 0,
    avgScore: 0,
  });

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);

      // Fetch all analyses
      const analysesRes = await analysisAPI.list();
      const analysesData = analysesRes.data;
      setAnalyses(analysesData);

      // Fetch all repositories for lookup
      const reposRes = await repositoryAPI.list();
      const reposMap = {};
      reposRes.data.forEach((repo) => {
        reposMap[repo.id] = repo;
      });
      setRepositories(reposMap);

      // Calculate statistics
      const completed = analysesData.filter((a) => a.status === 'completed');
      const avgScore =
        completed.length > 0
          ? completed.reduce((sum, a) => sum + (a.overall_score || 0), 0) / completed.length
          : 0;

      setStats({
        total: analysesData.length,
        completed: completed.length,
        running: analysesData.filter((a) => a.status === 'running').length,
        failed: analysesData.filter((a) => a.status === 'failed').length,
        avgScore: avgScore.toFixed(1),
      });
    } catch (error) {
      console.error('Error fetching data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleChangePage = (event, newPage) => {
    setPage(newPage);
  };

  const handleChangeRowsPerPage = (event) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };

  const handleMenuOpen = (event, analysis) => {
    setAnchorEl(event.currentTarget);
    setSelectedAnalysis(analysis);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
    setSelectedAnalysis(null);
  };

  const handleView = (analysis) => {
    navigate(`/analysis/${analysis.id}`);
    handleMenuClose();
  };

  const handleDelete = async (analysis) => {
    if (window.confirm('Are you sure you want to delete this analysis?')) {
      try {
        await analysisAPI.delete(analysis.id);
        fetchData();
      } catch (error) {
        console.error('Error deleting analysis:', error);
      }
    }
    handleMenuClose();
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

  const getStatusIcon = (status) => {
    const icons = {
      completed: <CheckCircle />,
      running: <HourglassEmpty />,
      pending: <HourglassEmpty />,
      failed: <Error />,
    };
    return icons[status] || <HourglassEmpty />;
  };

  const getScoreColor = (score) => {
    if (score >= 80) return 'success';
    if (score >= 60) return 'warning';
    return 'error';
  };

  // Filter analyses
  const filteredAnalyses = analyses.filter((analysis) => {
    const matchesStatus = filterStatus === 'all' || analysis.status === filterStatus;
    const matchesRepo = filterRepo === 'all' || analysis.repository_id === parseInt(filterRepo);
    const matchesSearch =
      !searchQuery ||
      repositories[analysis.repository_id]?.name.toLowerCase().includes(searchQuery.toLowerCase());

    return matchesStatus && matchesRepo && matchesSearch;
  });

  // Paginate
  const paginatedAnalyses = filteredAnalyses.slice(
    page * rowsPerPage,
    page * rowsPerPage + rowsPerPage
  );

  return (
    <Container maxWidth="xl">
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4">Analysis History</Typography>
        <Button
          variant="outlined"
          startIcon={<RefreshIcon />}
          onClick={fetchData}
          disabled={loading}
        >
          Refresh
        </Button>
      </Box>

      {/* Statistics Cards */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={2.4}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" mb={1}>
                <Assessment sx={{ mr: 1, color: '#2196f3' }} />
                <Typography variant="h6" fontSize="0.9rem">
                  Total Analyses
                </Typography>
              </Box>
              <Typography variant="h3" color="primary">
                {stats.total}
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={2.4}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" mb={1}>
                <CheckCircle sx={{ mr: 1, color: '#4caf50' }} />
                <Typography variant="h6" fontSize="0.9rem">
                  Completed
                </Typography>
              </Box>
              <Typography variant="h3" color="success.main">
                {stats.completed}
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={2.4}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" mb={1}>
                <HourglassEmpty sx={{ mr: 1, color: '#ff9800' }} />
                <Typography variant="h6" fontSize="0.9rem">
                  Running
                </Typography>
              </Box>
              <Typography variant="h3" color="warning.main">
                {stats.running}
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={2.4}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" mb={1}>
                <Error sx={{ mr: 1, color: '#f44336' }} />
                <Typography variant="h6" fontSize="0.9rem">
                  Failed
                </Typography>
              </Box>
              <Typography variant="h3" color="error.main">
                {stats.failed}
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={2.4}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" mb={1}>
                <TrendingUp sx={{ mr: 1, color: '#9c27b0' }} />
                <Typography variant="h6" fontSize="0.9rem">
                  Avg Score
                </Typography>
              </Box>
              <Typography variant="h3" color="secondary.main">
                {stats.avgScore}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Filters */}
      <Paper sx={{ p: 2, mb: 3 }}>
        <Grid container spacing={2} alignItems="center">
          <Grid item xs={12} md={4}>
            <TextField
              fullWidth
              label="Search by repository"
              variant="outlined"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              size="small"
            />
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <FormControl fullWidth size="small">
              <InputLabel>Status</InputLabel>
              <Select
                value={filterStatus}
                label="Status"
                onChange={(e) => setFilterStatus(e.target.value)}
              >
                <MenuItem value="all">All Statuses</MenuItem>
                <MenuItem value="completed">Completed</MenuItem>
                <MenuItem value="running">Running</MenuItem>
                <MenuItem value="pending">Pending</MenuItem>
                <MenuItem value="failed">Failed</MenuItem>
              </Select>
            </FormControl>
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <FormControl fullWidth size="small">
              <InputLabel>Repository</InputLabel>
              <Select
                value={filterRepo}
                label="Repository"
                onChange={(e) => setFilterRepo(e.target.value)}
              >
                <MenuItem value="all">All Repositories</MenuItem>
                {Object.values(repositories).map((repo) => (
                  <MenuItem key={repo.id} value={repo.id}>
                    {repo.name}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>

          <Grid item xs={12} md={2}>
            <Typography variant="body2" color="text.secondary">
              {filteredAnalyses.length} results
            </Typography>
          </Grid>
        </Grid>
      </Paper>

      {/* Analyses Table */}
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>ID</TableCell>
              <TableCell>Repository</TableCell>
              <TableCell>Status</TableCell>
              <TableCell>Overall Score</TableCell>
              <TableCell>Duration</TableCell>
              <TableCell>Created At</TableCell>
              <TableCell align="right">Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {loading ? (
              <TableRow>
                <TableCell colSpan={7} align="center">
                  Loading...
                </TableCell>
              </TableRow>
            ) : paginatedAnalyses.length === 0 ? (
              <TableRow>
                <TableCell colSpan={7} align="center">
                  No analyses found
                </TableCell>
              </TableRow>
            ) : (
              paginatedAnalyses.map((analysis) => {
                const repo = repositories[analysis.repository_id];

                return (
                  <TableRow key={analysis.id} hover sx={{ cursor: 'pointer' }}>
                    <TableCell onClick={() => handleView(analysis)}>#{analysis.id}</TableCell>
                    <TableCell onClick={() => handleView(analysis)}>
                      <Box>
                        <Typography variant="body2" fontWeight="bold">
                          {repo?.name || 'Unknown'}
                        </Typography>
                        {repo?.language && (
                          <Chip label={repo.language} size="small" sx={{ mt: 0.5 }} />
                        )}
                      </Box>
                    </TableCell>
                    <TableCell onClick={() => handleView(analysis)}>
                      <Chip
                        icon={getStatusIcon(analysis.status)}
                        label={analysis.status}
                        color={getStatusColor(analysis.status)}
                        size="small"
                      />
                    </TableCell>
                    <TableCell onClick={() => handleView(analysis)}>
                      {analysis.overall_score != null ? (
                        <Chip
                          label={`${analysis.overall_score.toFixed(0)}/100`}
                          color={getScoreColor(analysis.overall_score)}
                          size="small"
                        />
                      ) : (
                        '-'
                      )}
                    </TableCell>
                    <TableCell onClick={() => handleView(analysis)}>
                      {analysis.analysis_duration
                        ? `${analysis.analysis_duration.toFixed(1)}s`
                        : '-'}
                    </TableCell>
                    <TableCell onClick={() => handleView(analysis)}>
                      {new Date(analysis.created_at).toLocaleString()}
                    </TableCell>
                    <TableCell align="right">
                      <Tooltip title="View Details">
                        <IconButton size="small" onClick={() => handleView(analysis)}>
                          <Visibility />
                        </IconButton>
                      </Tooltip>
                      <Tooltip title="More Actions">
                        <IconButton
                          size="small"
                          onClick={(e) => handleMenuOpen(e, analysis)}
                        >
                          <MoreVert />
                        </IconButton>
                      </Tooltip>
                    </TableCell>
                  </TableRow>
                );
              })
            )}
          </TableBody>
        </Table>

        <TablePagination
          rowsPerPageOptions={[5, 10, 25, 50, 100]}
          component="div"
          count={filteredAnalyses.length}
          rowsPerPage={rowsPerPage}
          page={page}
          onPageChange={handleChangePage}
          onRowsPerPageChange={handleChangeRowsPerPage}
        />
      </TableContainer>

      {/* Context Menu */}
      <Menu anchorEl={anchorEl} open={Boolean(anchorEl)} onClose={handleMenuClose}>
        <MenuItem onClick={() => handleView(selectedAnalysis)}>
          <ListItemIcon>
            <Visibility fontSize="small" />
          </ListItemIcon>
          <ListItemText>View Details</ListItemText>
        </MenuItem>
        <MenuItem onClick={() => handleDelete(selectedAnalysis)}>
          <ListItemIcon>
            <Delete fontSize="small" color="error" />
          </ListItemIcon>
          <ListItemText>Delete</ListItemText>
        </MenuItem>
      </Menu>
    </Container>
  );
}
