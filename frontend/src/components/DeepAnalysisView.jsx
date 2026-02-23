import React, { useState } from 'react';
import {
  Box,
  Typography,
  Alert,
  Tab,
  Tabs,
  Paper,
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

const DeepAnalysisView = ({ deepAnalysis }) => {
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

  return (
    <Box sx={{ width: '100%' }}>
      {/* Premium Feature Banner */}
      <Box sx={{
        mb: 3, p: 3, borderRadius: 2,
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        color: 'white',
        boxShadow: '0 4px 20px rgba(102, 126, 234, 0.3)',
        position: 'relative', overflow: 'hidden',
        '&::before': {
          content: '""', position: 'absolute', top: 0, right: 0,
          width: '200px', height: '200px',
          background: 'radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%)',
          borderRadius: '50%', transform: 'translate(50%, -50%)',
        },
      }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, position: 'relative' }}>
          <ScienceIcon sx={{ fontSize: 48 }} />
          <Box>
            <Typography variant="h5" sx={{ fontWeight: 700, mb: 0.5 }}>
              Multi-Stage Deep Analysis Complete
            </Typography>
            <Typography variant="body1" sx={{ opacity: 0.95 }}>
              Premium analysis examined 5 architectural layers with AI-powered insights
            </Typography>
          </Box>
        </Box>
      </Box>

      {/* Tab Navigation */}
      <Paper sx={{ width: '100%', mb: 2, borderRadius: 2, overflow: 'hidden', boxShadow: '0 2px 8px rgba(0,0,0,0.1)' }}>
        <Tabs
          value={activeTab}
          onChange={(e, v) => setActiveTab(v)}
          variant="scrollable"
          scrollButtons="auto"
          sx={{
            '& .MuiTab-root': { fontWeight: 600, minHeight: 64,
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
      <Box sx={{ p: 3 }}>
        {activeTab === 0 && <SynthesisSection synthesis={synthesis} />}
        {LAYER_TABS.map((t, i) =>
          activeTab === i + 1 ? (
            <LayerAnalysisTab key={t.layer} layerName={t.layer} layerData={layers[t.layer]} />
          ) : null
        )}
      </Box>
    </Box>
  );
};

export default DeepAnalysisView;
