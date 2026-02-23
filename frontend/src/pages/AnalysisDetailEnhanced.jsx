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

  return (
    <Container maxWidth="xl">
      {/* Header */}
      <Box display="flex" alignItems="center" mb={3}>
        <Button startIcon={<ArrowBack />} onClick={() => navigate(-1)} sx={{ mr: 2 }}>
          Back
        </Button>
        <Typography variant="h4" sx={{ flexGrow: 1 }}>
          Code Analysis Report
        </Typography>
        <Chip
          label={getScoreGrade(analysis.overall_score || 0)}
          color={getStatusColor(analysis.status)}
          sx={{ fontSize: '1.2rem', px: 2, py: 3, mr: 2 }}
        />
        <Button startIcon={<Refresh />} onClick={() => fetchAnalysis()} variant="outlined">
          Refresh
        </Button>
      </Box>

      {/* Repository Info Banner */}
      {repository && (
        <Alert severity="info" sx={{ mb: 3 }} icon={<Assessment />}>
          <Typography variant="h6">{repository.name}</Typography>
          <Typography variant="body2">{repository.description || 'No description'}</Typography>
          <Box mt={1}>
            <Chip label={repository.source} size="small" sx={{ mr: 1 }} />
            {repository.language && <Chip label={repository.language} size="small" />}
          </Box>
        </Alert>
      )}

      {/* Status Banners */}
      {analysis.status === 'running' && (
        <Alert severity="info" sx={{ mb: 3 }}>
          <Typography variant="body1">Analysis in progress...</Typography>
          <CircularProgress size={20} sx={{ ml: 2 }} />
        </Alert>
      )}

      {analysis.status === 'failed' && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {analysis.error_message || 'Analysis failed'}
        </Alert>
      )}

      {analysis.status === 'completed' && (
        <>
          {/* Tab Bar */}
          <Paper sx={{ mb: 3 }}>
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
          {activeTab === 1 && <DeepAnalysisView deepAnalysis={analysis.detailed_report?.deep_analysis} />}
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
    </Container>
  );
}
