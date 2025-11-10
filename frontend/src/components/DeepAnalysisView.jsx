import React, { useState } from 'react';
import {
  Box,
  Typography,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Chip,
  Alert,
  Card,
  CardContent,
  Grid,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Tab,
  Tabs,
  Paper,
  Divider,
  Tooltip,
  IconButton,
} from '@mui/material';
import {
  ExpandMore as ExpandMoreIcon,
  Security as SecurityIcon,
  Speed as PerformanceIcon,
  BugReport as TestingIcon,
  Cloud as DevOpsIcon,
  Code as CodeQualityIcon,
  CheckCircle as CheckCircleIcon,
  Warning as WarningIcon,
  Error as ErrorIcon,
  Info as InfoIcon,
  TrendingUp as TrendingUpIcon,
  AccessTime as TimeIcon,
  Build as BuildIcon,
} from '@mui/icons-material';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

const DeepAnalysisView = ({ deepAnalysis }) => {
  const [activeTab, setActiveTab] = useState(0);
  const [expandedPanel, setExpandedPanel] = useState(false);

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

  // Priority color mapping
  const getPriorityColor = (priority) => {
    switch (priority?.toLowerCase()) {
      case 'critical':
        return 'error';
      case 'high':
        return 'warning';
      case 'medium':
        return 'info';
      case 'low':
        return 'success';
      default:
        return 'default';
    }
  };

  // Layer icon mapping
  const getLayerIcon = (layerName) => {
    switch (layerName) {
      case 'security':
        return <SecurityIcon />;
      case 'performance':
        return <PerformanceIcon />;
      case 'testing':
        return <TestingIcon />;
      case 'devops':
        return <DevOpsIcon />;
      case 'code_quality':
        return <CodeQualityIcon />;
      default:
        return <InfoIcon />;
    }
  };

  // Render issue card
  const renderIssue = (issue, index) => (
    <Card key={index} sx={{ mb: 2, borderLeft: `4px solid ${
      issue.priority === 'Critical' ? '#f44336' :
      issue.priority === 'High' ? '#ff9800' :
      issue.priority === 'Medium' ? '#2196f3' : '#4caf50'
    }` }}>
      <CardContent>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 1 }}>
          <Typography variant="h6" sx={{ flex: 1 }}>
            {issue.issue || issue.message || 'Issue'}
          </Typography>
          <Chip
            label={issue.priority || 'Medium'}
            color={getPriorityColor(issue.priority)}
            size="small"
          />
        </Box>

        {issue.location && (
          <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
            <strong>Location:</strong> <code>{issue.location}</code>
          </Typography>
        )}

        {issue.evidence && (
          <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
            <strong>Evidence:</strong> {issue.evidence}
          </Typography>
        )}

        {(issue.fix || issue.refactoring) && (
          <Alert severity="success" sx={{ mt: 2 }}>
            <Typography variant="body2">
              <strong>Fix:</strong> {issue.fix || issue.refactoring}
            </Typography>
          </Alert>
        )}

        {issue.expected_improvement && (
          <Typography variant="body2" color="primary" sx={{ mt: 1 }}>
            <TrendingUpIcon fontSize="small" sx={{ verticalAlign: 'middle', mr: 0.5 }} />
            <strong>Expected Impact:</strong> {issue.expected_improvement}
          </Typography>
        )}

        {issue.effort_hours && (
          <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
            <TimeIcon fontSize="small" sx={{ verticalAlign: 'middle', mr: 0.5 }} />
            <strong>Effort:</strong> {issue.effort_hours} hours
          </Typography>
        )}

        {issue.business_impact && (
          <Typography variant="body2" color="error" sx={{ mt: 1 }}>
            <strong>Business Impact:</strong> {issue.business_impact}
          </Typography>
        )}
      </CardContent>
    </Card>
  );

  // Render layer-specific findings
  const renderLayerFindings = (layerName, layerData) => {
    if (!layerData || layerData.error) {
      return (
        <Alert severity="warning">
          <Typography>
            {layerName} analysis failed: {layerData?.error || 'Unknown error'}
          </Typography>
        </Alert>
      );
    }

    const issues = layerData.critical_issues || layerData.bottlenecks || layerData.coverage_gaps || layerData.missing_devops || layerData.quality_issues || [];
    const recommendations = layerData.recommendations || [];

    return (
      <Box>
        {/* Issues */}
        {issues.length > 0 ? (
          <Box sx={{ mb: 3 }}>
            <Typography variant="h6" sx={{ mb: 2 }}>
              {issues.length} {layerName === 'security' ? 'Security Issues' :
                layerName === 'performance' ? 'Performance Bottlenecks' :
                layerName === 'testing' ? 'Test Coverage Gaps' :
                layerName === 'devops' ? 'DevOps Gaps' :
                'Code Quality Issues'}
            </Typography>
            {issues.map((issue, index) => renderIssue(issue, index))}
          </Box>
        ) : (
          <Alert severity="success" sx={{ mb: 3 }}>
            <Typography>No critical issues found in {layerName} analysis!</Typography>
          </Alert>
        )}

        {/* Recommendations */}
        {recommendations.length > 0 && (
          <Box>
            <Typography variant="h6" sx={{ mb: 2 }}>
              Recommendations
            </Typography>
            <List>
              {recommendations.map((rec, index) => (
                <ListItem key={index}>
                  <ListItemIcon>
                    <BuildIcon color="primary" />
                  </ListItemIcon>
                  <ListItemText primary={rec} />
                </ListItem>
              ))}
            </List>
          </Box>
        )}

        {/* Raw analysis fallback - render as markdown */}
        {layerData.raw_analysis && issues.length === 0 && (
          <Paper sx={{ p: 3, bgcolor: '#f5f5f5' }}>
            <Typography variant="body2" sx={{ mb: 2, color: 'text.secondary' }}>
              <InfoIcon fontSize="small" sx={{ verticalAlign: 'middle', mr: 1 }} />
              AI Analysis Results (formatted view)
            </Typography>
            <Box sx={{
              '& h1, & h2, & h3': { mt: 2, mb: 1 },
              '& ul, & ol': { pl: 3 },
              '& li': { mb: 0.5 },
              '& p': { mb: 1 },
              '& code': {
                bgcolor: '#e0e0e0',
                px: 0.5,
                py: 0.25,
                borderRadius: 1,
                fontSize: '0.9em'
              },
              '& pre': {
                bgcolor: '#263238',
                color: '#fff',
                p: 2,
                borderRadius: 1,
                overflow: 'auto'
              }
            }}>
              <ReactMarkdown remarkPlugins={[remarkGfm]}>
                {layerData.raw_analysis}
              </ReactMarkdown>
            </Box>
          </Paper>
        )}
      </Box>
    );
  };

  // Render synthesis report
  const renderSynthesis = () => {
    if (!synthesis || synthesis.error) {
      return (
        <Alert severity="warning">
          <Typography>Synthesis report not available: {synthesis?.error || 'Unknown error'}</Typography>
        </Alert>
      );
    }

    // Check if we have structured data or raw analysis
    const hasStructuredData = synthesis.executive_summary ||
                               synthesis.critical_issues?.length > 0 ||
                               synthesis.high_priority?.length > 0 ||
                               synthesis.medium_priority?.length > 0 ||
                               synthesis.low_priority?.length > 0 ||
                               synthesis.quick_wins?.length > 0;

    // If no structured data, show the raw analysis
    if (!hasStructuredData) {
      const rawContent = typeof synthesis === 'string' ? synthesis : JSON.stringify(synthesis, null, 2);
      return (
        <Paper sx={{ p: 3 }}>
          <Alert severity="info" sx={{ mb: 2 }}>
            <Typography variant="body2">
              <InfoIcon fontSize="small" sx={{ verticalAlign: 'middle', mr: 1 }} />
              AI-Generated Analysis Report (formatted view)
            </Typography>
          </Alert>
          <Box sx={{
            '& h1, & h2, & h3': { mt: 2, mb: 1 },
            '& ul, & ol': { pl: 3 },
            '& li': { mb: 0.5 },
            '& p': { mb: 1 },
            '& code': {
              bgcolor: '#e0e0e0',
              px: 0.5,
              py: 0.25,
              borderRadius: 1,
              fontSize: '0.9em'
            },
            '& pre': {
              bgcolor: '#263238',
              color: '#fff',
              p: 2,
              borderRadius: 1,
              overflow: 'auto'
            }
          }}>
            <ReactMarkdown remarkPlugins={[remarkGfm]}>
              {rawContent}
            </ReactMarkdown>
          </Box>
        </Paper>
      );
    }

    return (
      <Box>
        {/* Executive Summary */}
        {synthesis.executive_summary && (
          <Alert severity="info" sx={{ mb: 3 }}>
            <Typography variant="h6" sx={{ mb: 1 }}>Executive Summary</Typography>
            <Typography variant="body1">{synthesis.executive_summary}</Typography>
          </Alert>
        )}

        {/* Quick Wins */}
        {synthesis.quick_wins && synthesis.quick_wins.length > 0 && (
          <Paper sx={{ p: 2, mb: 3, bgcolor: '#e8f5e9' }}>
            <Typography variant="h6" sx={{ mb: 2, display: 'flex', alignItems: 'center' }}>
              <CheckCircleIcon sx={{ mr: 1, color: '#4caf50' }} />
              Quick Wins ({"<"} 4 hours each)
            </Typography>
            <List>
              {synthesis.quick_wins.map((win, index) => (
                <ListItem key={index}>
                  <ListItemIcon>
                    <CheckCircleIcon color="success" />
                  </ListItemIcon>
                  <ListItemText primary={win} />
                </ListItem>
              ))}
            </List>
          </Paper>
        )}

        {/* Critical Issues */}
        {synthesis.critical_issues && synthesis.critical_issues.length > 0 && (
          <Accordion expanded={expandedPanel === 'critical'} onChange={() => setExpandedPanel(expandedPanel === 'critical' ? false : 'critical')}>
            <AccordionSummary expandIcon={<ExpandMoreIcon />} sx={{ bgcolor: '#ffebee' }}>
              <Box sx={{ display: 'flex', alignItems: 'center', width: '100%' }}>
                <ErrorIcon sx={{ mr: 1, color: '#f44336' }} />
                <Typography variant="h6">Critical Issues ({synthesis.critical_issues.length})</Typography>
                <Chip label="Fix Immediately" color="error" size="small" sx={{ ml: 2 }} />
              </Box>
            </AccordionSummary>
            <AccordionDetails>
              {synthesis.critical_issues.map((issue, index) => renderIssue(issue, index))}
            </AccordionDetails>
          </Accordion>
        )}

        {/* High Priority */}
        {synthesis.high_priority && synthesis.high_priority.length > 0 && (
          <Accordion expanded={expandedPanel === 'high'} onChange={() => setExpandedPanel(expandedPanel === 'high' ? false : 'high')} sx={{ mt: 1 }}>
            <AccordionSummary expandIcon={<ExpandMoreIcon />} sx={{ bgcolor: '#fff3e0' }}>
              <Box sx={{ display: 'flex', alignItems: 'center', width: '100%' }}>
                <WarningIcon sx={{ mr: 1, color: '#ff9800' }} />
                <Typography variant="h6">High Priority ({synthesis.high_priority.length})</Typography>
                <Chip label="1-2 Sprints" color="warning" size="small" sx={{ ml: 2 }} />
              </Box>
            </AccordionSummary>
            <AccordionDetails>
              {synthesis.high_priority.map((issue, index) => renderIssue(issue, index))}
            </AccordionDetails>
          </Accordion>
        )}

        {/* Medium Priority */}
        {synthesis.medium_priority && synthesis.medium_priority.length > 0 && (
          <Accordion expanded={expandedPanel === 'medium'} onChange={() => setExpandedPanel(expandedPanel === 'medium' ? false : 'medium')} sx={{ mt: 1 }}>
            <AccordionSummary expandIcon={<ExpandMoreIcon />} sx={{ bgcolor: '#e3f2fd' }}>
              <Box sx={{ display: 'flex', alignItems: 'center', width: '100%' }}>
                <InfoIcon sx={{ mr: 1, color: '#2196f3' }} />
                <Typography variant="h6">Medium Priority ({synthesis.medium_priority.length})</Typography>
                <Chip label="1-2 Months" color="info" size="small" sx={{ ml: 2 }} />
              </Box>
            </AccordionSummary>
            <AccordionDetails>
              {synthesis.medium_priority.map((issue, index) => renderIssue(issue, index))}
            </AccordionDetails>
          </Accordion>
        )}

        {/* Low Priority */}
        {synthesis.low_priority && synthesis.low_priority.length > 0 && (
          <Accordion expanded={expandedPanel === 'low'} onChange={() => setExpandedPanel(expandedPanel === 'low' ? false : 'low')} sx={{ mt: 1 }}>
            <AccordionSummary expandIcon={<ExpandMoreIcon />} sx={{ bgcolor: '#f1f8e9' }}>
              <Box sx={{ display: 'flex', alignItems: 'center', width: '100%' }}>
                <CheckCircleIcon sx={{ mr: 1, color: '#4caf50' }} />
                <Typography variant="h6">Low Priority ({synthesis.low_priority.length})</Typography>
                <Chip label="Nice to Have" color="success" size="small" sx={{ ml: 2 }} />
              </Box>
            </AccordionSummary>
            <AccordionDetails>
              {synthesis.low_priority.map((issue, index) => renderIssue(issue, index))}
            </AccordionDetails>
          </Accordion>
        )}

        {/* Effort Estimate */}
        {synthesis.estimated_total_effort_days && (
          <Alert severity="info" sx={{ mt: 3 }}>
            <Typography variant="body1">
              <strong>Estimated Total Effort:</strong> {synthesis.estimated_total_effort_days} days
            </Typography>
          </Alert>
        )}
      </Box>
    );
  };

  return (
    <Box sx={{ width: '100%' }}>
      <Alert severity="success" sx={{ mb: 3 }}>
        <Typography variant="body1">
          <strong>Multi-Stage Deep Analysis Complete!</strong> This premium analysis examined 5 architectural layers
          (Security, Performance, Testing, DevOps, Code Quality) and generated specific findings with exact locations and fixes.
        </Typography>
      </Alert>

      <Paper sx={{ width: '100%', mb: 2 }}>
        <Tabs
          value={activeTab}
          onChange={(e, newValue) => setActiveTab(newValue)}
          variant="scrollable"
          scrollButtons="auto"
        >
          <Tab label="📊 Synthesis Report" />
          <Tab label="🔒 Security" icon={<SecurityIcon />} iconPosition="start" />
          <Tab label="⚡ Performance" icon={<PerformanceIcon />} iconPosition="start" />
          <Tab label="🧪 Testing" icon={<TestingIcon />} iconPosition="start" />
          <Tab label="☁️ DevOps" icon={<DevOpsIcon />} iconPosition="start" />
          <Tab label="💎 Code Quality" icon={<CodeQualityIcon />} iconPosition="start" />
        </Tabs>
      </Paper>

      <Box sx={{ p: 3 }}>
        {/* Synthesis Report Tab */}
        {activeTab === 0 && renderSynthesis()}

        {/* Security Tab */}
        {activeTab === 1 && renderLayerFindings('security', layers.security)}

        {/* Performance Tab */}
        {activeTab === 2 && renderLayerFindings('performance', layers.performance)}

        {/* Testing Tab */}
        {activeTab === 3 && renderLayerFindings('testing', layers.testing)}

        {/* DevOps Tab */}
        {activeTab === 4 && renderLayerFindings('devops', layers.devops)}

        {/* Code Quality Tab */}
        {activeTab === 5 && renderLayerFindings('code_quality', layers.code_quality)}
      </Box>
    </Box>
  );
};

export default DeepAnalysisView;
