import { useState } from 'react';
import {
  Box,
  Typography,
  Alert,
  Tab,
  Tabs,
  Paper,
  Chip,
} from '@mui/material';
import {
  TrendingUp as TrendingUpIcon,
  Shield as ShieldIcon,
  Bolt as BoltIcon,
  Science as ScienceIcon,
  Rocket as RocketIcon,
  Diamond as DiamondIcon,
} from '@mui/icons-material';
import SynthesisSection from './deep-analysis/SynthesisSection';
import LayerAnalysisTab from './deep-analysis/LayerAnalysisTab';

const LAYER_TABS = [
  { label: 'Security',     icon: <ShieldIcon />,   layer: 'security' },
  { label: 'Performance',  icon: <BoltIcon />,     layer: 'performance' },
  { label: 'Testing',      icon: <ScienceIcon />,  layer: 'testing' },
  { label: 'DevOps',       icon: <RocketIcon />,   layer: 'devops' },
  { label: 'Code Quality', icon: <DiamondIcon />,  layer: 'code_quality' },
];

const DeepAnalysisView = ({ deepAnalysis, analysisId, repoUrl, onIssueStatusChange }) => {
  const [activeTab, setActiveTab] = useState(0);

  if (!deepAnalysis || !deepAnalysis.analysis_completed) {
    return (
      <Alert severity="info">
        <Typography variant="body1">
          Deep analysis data is not available or analysis is still in progress.
        </Typography>
      </Alert>
    );
  }

  const { layers, synthesis } = deepAnalysis;
  const issueStatuses = deepAnalysis.issue_statuses || {};

  return (
    <Box sx={{ width: '100%' }}>
      {/* Compact status chip */}
      <Box sx={{ mb: 1.5, display: 'flex', alignItems: 'center', gap: 1 }}>
        <Chip
          icon={<ScienceIcon />}
          label="Multi-Stage Deep Analysis Complete — 5 Layers"
          sx={{
            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            color: 'white',
            fontWeight: 600,
            '& .MuiChip-icon': { color: 'white' },
          }}
        />
      </Box>

      {/* Tab Navigation */}
      <Paper sx={{ width: '100%', mb: 1.5, borderRadius: 2, overflow: 'hidden', boxShadow: '0 2px 8px rgba(0,0,0,0.1)' }}>
        <Tabs
          value={activeTab}
          onChange={(e, v) => setActiveTab(v)}
          variant="scrollable"
          scrollButtons="auto"
          sx={{
            '& .MuiTab-root': { fontWeight: 600, minHeight: 48,
              '&.Mui-selected': { background: 'linear-gradient(135deg, rgba(102,126,234,0.1) 0%, rgba(118,75,162,0.1) 100%)' },
            },
            '& .MuiTabs-indicator': { height: 3, background: 'linear-gradient(90deg, #667eea 0%, #764ba2 100%)' },
          }}
        >
          <Tab label="Synthesis Report" icon={<TrendingUpIcon />} iconPosition="start" sx={{ gap: 1 }} />
          {LAYER_TABS.map((t) => (
            <Tab key={t.layer} label={t.label} icon={t.icon} iconPosition="start" sx={{ gap: 1 }} />
          ))}
        </Tabs>
      </Paper>

      {/* Tab Content */}
      <Box sx={{ pt: 1 }}>
        {activeTab === 0 && (
          <SynthesisSection
            synthesis={synthesis}
            issueStatuses={issueStatuses}
            repoUrl={repoUrl}
            onIssueStatusChange={onIssueStatusChange}
          />
        )}
        {LAYER_TABS.map((t, i) =>
          activeTab === i + 1 ? (
            <LayerAnalysisTab
              key={t.layer}
              layerName={t.layer}
              layerData={layers[t.layer]}
              issueStatuses={issueStatuses}
              repoUrl={repoUrl}
              onIssueStatusChange={onIssueStatusChange}
            />
          ) : null
        )}
      </Box>
    </Box>
  );
};

export default DeepAnalysisView;
