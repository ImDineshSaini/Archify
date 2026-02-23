import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Container, Typography, Box, Button } from '@mui/material';
import { Refresh as RefreshIcon } from '@mui/icons-material';
import { analysisAPI, repositoryAPI } from '../services/api';
import StatsCards from './analysis-history/StatsCards';
import FiltersBar from './analysis-history/FiltersBar';
import AnalysisTable from './analysis-history/AnalysisTable';

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
  const [stats, setStats] = useState({ total: 0, completed: 0, running: 0, failed: 0, avgScore: 0 });

  useEffect(() => { fetchData(); }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      const analysesRes = await analysisAPI.list();
      const analysesData = analysesRes.data;
      setAnalyses(analysesData);

      const reposRes = await repositoryAPI.list();
      const reposMap = {};
      reposRes.data.forEach((repo) => { reposMap[repo.id] = repo; });
      setRepositories(reposMap);

      const completed = analysesData.filter((a) => a.status === 'completed');
      const avgScore = completed.length > 0
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

  const handleMenuOpen = (event, analysis) => { setAnchorEl(event.currentTarget); setSelectedAnalysis(analysis); };
  const handleMenuClose = () => { setAnchorEl(null); setSelectedAnalysis(null); };
  const handleView = (analysis) => { navigate(`/analysis/${analysis.id}`); handleMenuClose(); };
  const handleDelete = async (analysis) => {
    if (window.confirm('Are you sure you want to delete this analysis?')) {
      try { await analysisAPI.delete(analysis.id); fetchData(); } catch (error) { console.error('Error deleting analysis:', error); }
    }
    handleMenuClose();
  };

  const filteredAnalyses = analyses.filter((analysis) => {
    const matchesStatus = filterStatus === 'all' || analysis.status === filterStatus;
    const matchesRepo = filterRepo === 'all' || analysis.repository_id === parseInt(filterRepo);
    const matchesSearch = !searchQuery || repositories[analysis.repository_id]?.name.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesStatus && matchesRepo && matchesSearch;
  });

  const paginatedAnalyses = filteredAnalyses.slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage);

  return (
    <Container maxWidth="xl">
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4">Analysis History</Typography>
        <Button variant="outlined" startIcon={<RefreshIcon />} onClick={fetchData} disabled={loading}>
          Refresh
        </Button>
      </Box>

      <StatsCards stats={stats} />

      <FiltersBar
        searchQuery={searchQuery}
        onSearchChange={setSearchQuery}
        filterStatus={filterStatus}
        onFilterStatusChange={setFilterStatus}
        filterRepo={filterRepo}
        onFilterRepoChange={setFilterRepo}
        repositories={repositories}
        resultCount={filteredAnalyses.length}
      />

      <AnalysisTable
        loading={loading}
        paginatedAnalyses={paginatedAnalyses}
        repositories={repositories}
        filteredCount={filteredAnalyses.length}
        page={page}
        rowsPerPage={rowsPerPage}
        onPageChange={(e, newPage) => setPage(newPage)}
        onRowsPerPageChange={(e) => { setRowsPerPage(parseInt(e.target.value, 10)); setPage(0); }}
        onView={handleView}
        onDelete={handleDelete}
        anchorEl={anchorEl}
        selectedAnalysis={selectedAnalysis}
        onMenuOpen={handleMenuOpen}
        onMenuClose={handleMenuClose}
      />
    </Container>
  );
}
