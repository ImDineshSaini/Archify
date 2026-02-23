import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Container,
  Typography,
  Box,
  Paper,
  Chip,
  CircularProgress,
  Button,
  Alert,
  Tab,
  Tabs,
} from '@mui/material';
import {
  ArrowBack,
  Refresh,
  TrendingUp,
  Lightbulb,
  Build,
  Assessment,
  Layers as LayersIcon,
} from '@mui/icons-material';
import { analysisAPI, repositoryAPI } from '../services/api';
import { Snackbar } from '@mui/material';
import NFRAnalysisView from '../components/NFRAnalysisView';
import DeepAnalysisView from '../components/DeepAnalysisView';
import { getStatusColor, getScoreGrade } from '../utils/statusColors';

import ExecutiveSummaryTab from './analysis/ExecutiveSummaryTab';
import DetailedMetricsTab from './analysis/DetailedMetricsTab';
import AIInsightsTab from './analysis/AIInsightsTab';
import CodeQualityTab from './analysis/CodeQualityTab';

export default function AnalysisDetailEnhanced() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [analysis, setAnalysis] = useState(null);
  const [repository, setRepository] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState(0);
  const [expandedMetric, setExpandedMetric] = useState(null);
  const [snackbar, setSnackbar] = useState(null);

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

  const handleIssueStatusChange = async (layer, issueIndex, status) => {
    try {
      await analysisAPI.updateIssueStatus(id, { layer, issue_index: issueIndex, status });
      // Update local state to reflect the change immediately
      setAnalysis((prev) => {
        const updated = { ...prev };
        const report = { ...(updated.detailed_report || {}) };
        const statuses = { ...(report.deep_analysis?.issue_statuses || {}) };
        statuses[`${layer}:${issueIndex}`] = status;
        report.deep_analysis = { ...(report.deep_analysis || {}), issue_statuses: statuses };
        updated.detailed_report = report;
        return updated;
      });
      setSnackbar(`Issue marked as ${status.replace('_', ' ')}`);
    } catch (error) {
      console.error('Error updating issue status:', error);
      setSnackbar('Failed to update issue status');
    }
  };

  if (loading || !analysis) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Container maxWidth="xl">
      {/* Compact Header */}
      <Box display="flex" alignItems="center" mb={1.5} flexWrap="wrap" gap={1}>
        <Button startIcon={<ArrowBack />} onClick={() => navigate(-1)} size="small">
          Back
        </Button>
        <Typography variant="h5" sx={{ fontWeight: 700 }}>
          {repository?.name || 'Analysis Report'}
        </Typography>
        {repository?.source && <Chip label={repository.source} size="small" variant="outlined" />}
        {repository?.language && <Chip label={repository.language} size="small" variant="outlined" />}
        <Chip
          label={getScoreGrade(analysis.overall_score || 0)}
          color={getStatusColor(analysis.status)}
          sx={{ fontWeight: 700 }}
        />
        <Box sx={{ flexGrow: 1 }} />
        <Button startIcon={<Refresh />} onClick={() => fetchAnalysis()} variant="outlined" size="small">
          Refresh
        </Button>
      </Box>

      {/* Status Banners */}
      {analysis.status === 'running' && (
        <Alert severity="info" sx={{ mb: 1.5 }}>
          <Typography variant="body1">Analysis in progress...</Typography>
          <CircularProgress size={20} sx={{ ml: 2 }} />
        </Alert>
      )}

      {analysis.status === 'failed' && (
        <Alert severity="error" sx={{ mb: 1.5 }}>
          {analysis.error_message || 'Analysis failed'}
        </Alert>
      )}

      {analysis.status === 'completed' && (
        <>
          {/* Tab Bar */}
          <Paper sx={{ mb: 1.5 }}>
            <Tabs value={activeTab} onChange={(e, v) => setActiveTab(v)} variant="scrollable" scrollButtons="auto">
              <Tab label="Executive Summary" icon={<TrendingUp />} iconPosition="start" />
              <Tab label="Deep Analysis" icon={<LayersIcon />} iconPosition="start" />
              <Tab label="NFR Analysis (40+)" icon={<Assessment />} iconPosition="start" />
              <Tab label="Detailed Metrics" icon={<Assessment />} iconPosition="start" />
              <Tab label="AI Insights" icon={<Lightbulb />} iconPosition="start" />
              <Tab label="Code Quality" icon={<Build />} iconPosition="start" />
            </Tabs>
          </Paper>

          {/* Tab Content */}
          {activeTab === 0 && <ExecutiveSummaryTab analysis={analysis} />}
          {activeTab === 1 && (
            <DeepAnalysisView
              deepAnalysis={analysis.detailed_report?.deep_analysis}
              analysisId={analysis.id}
              repoUrl={repository?.url}
              onIssueStatusChange={handleIssueStatusChange}
            />
          )}
          {activeTab === 2 && <NFRAnalysisView nfrAnalysis={analysis.detailed_report?.nfr_analysis} />}
          {activeTab === 3 && (
            <DetailedMetricsTab
              analysis={analysis}
              expandedMetric={expandedMetric}
              setExpandedMetric={setExpandedMetric}
            />
          )}
          {activeTab === 4 && <AIInsightsTab analysis={analysis} />}
          {activeTab === 5 && <CodeQualityTab analysis={analysis} />}
        </>
      )}

      <Snackbar
        open={Boolean(snackbar)}
        autoHideDuration={3000}
        onClose={() => setSnackbar(null)}
        message={snackbar}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
      />
    </Container>
  );
}
