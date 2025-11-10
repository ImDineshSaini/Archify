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
  FlashOn as FlashOnIcon,
  Shield as ShieldIcon,
  Bolt as BoltIcon,
  Science as ScienceIcon,
  Rocket as RocketIcon,
  Diamond as DiamondIcon,
  Star as StarIcon,
  LocalFireDepartment as FireIcon,
  EmojiEvents as TrophyIcon,
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

  // Priority icon mapping
  const getPriorityIcon = (priority) => {
    switch (priority?.toLowerCase()) {
      case 'critical':
        return <FireIcon sx={{ fontSize: 20 }} />;
      case 'high':
        return <BoltIcon sx={{ fontSize: 20 }} />;
      case 'medium':
        return <StarIcon sx={{ fontSize: 20 }} />;
      case 'low':
        return <TrophyIcon sx={{ fontSize: 20 }} />;
      default:
        return <InfoIcon sx={{ fontSize: 20 }} />;
    }
  };

  // Priority gradient colors
  const getPriorityGradient = (priority) => {
    switch (priority?.toLowerCase()) {
      case 'critical':
        return 'linear-gradient(135deg, #d32f2f 0%, #c62828 100%)';
      case 'high':
        return 'linear-gradient(135deg, #f57c00 0%, #e65100 100%)';
      case 'medium':
        return 'linear-gradient(135deg, #1976d2 0%, #0d47a1 100%)';
      case 'low':
        return 'linear-gradient(135deg, #388e3c 0%, #2e7d32 100%)';
      default:
        return 'linear-gradient(135deg, #757575 0%, #616161 100%)';
    }
  };

  // Render issue card
  const renderIssue = (issue, index) => (
    <Card key={index} sx={{
      mb: 2,
      borderLeft: `5px solid ${
        issue.priority === 'Critical' ? '#d32f2f' :
        issue.priority === 'High' ? '#f57c00' :
        issue.priority === 'Medium' ? '#1976d2' : '#388e3c'
      }`,
      boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
      transition: 'transform 0.2s, box-shadow 0.2s',
      '&:hover': {
        transform: 'translateY(-2px)',
        boxShadow: '0 4px 16px rgba(0,0,0,0.15)'
      }
    }}>
      <CardContent>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 1 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', flex: 1, gap: 1 }}>
            {getPriorityIcon(issue.priority)}
            <Typography variant="h6" sx={{ flex: 1 }}>
              {issue.issue || issue.message || 'Issue'}
            </Typography>
          </Box>
          <Chip
            label={issue.priority || 'Medium'}
            sx={{
              background: getPriorityGradient(issue.priority),
              color: 'white',
              fontWeight: 600,
              boxShadow: '0 2px 4px rgba(0,0,0,0.2)'
            }}
            size="small"
          />
        </Box>

        {issue.location && (
          <Box sx={{ mb: 1, p: 1, bgcolor: '#f5f5f5', borderRadius: 1 }}>
            <Typography variant="body2" sx={{ fontFamily: 'monospace' }}>
              <strong>📍 Location:</strong> <code style={{ color: '#d32f2f' }}>{issue.location}</code>
            </Typography>
          </Box>
        )}

        {issue.evidence && (
          <Typography variant="body2" color="text.secondary" sx={{ mb: 1, pl: 2, borderLeft: '3px solid #e0e0e0' }}>
            <strong>🔍 Evidence:</strong> {issue.evidence}
          </Typography>
        )}

        {(issue.fix || issue.refactoring) && (
          <Box sx={{
            mt: 2,
            p: 2,
            borderRadius: 2,
            background: 'linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 100%)',
            border: '1px solid #a5d6a7'
          }}>
            <Typography variant="body2" sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <BuildIcon sx={{ color: '#2e7d32', fontSize: 20 }} />
              <strong>Fix:</strong>
            </Typography>
            <Typography variant="body2" sx={{ mt: 0.5, pl: 3 }}>
              {issue.fix || issue.refactoring}
            </Typography>
          </Box>
        )}

        {issue.expected_improvement && (
          <Box sx={{ mt: 1, display: 'flex', alignItems: 'center', gap: 1, p: 1, bgcolor: '#e3f2fd', borderRadius: 1 }}>
            <RocketIcon sx={{ color: '#1976d2', fontSize: 20 }} />
            <Typography variant="body2" sx={{ fontWeight: 500 }}>
              <strong>Expected Impact:</strong> {issue.expected_improvement}
            </Typography>
          </Box>
        )}

        {issue.effort_hours && (
          <Box sx={{ mt: 1, display: 'flex', alignItems: 'center', gap: 1 }}>
            <TimeIcon fontSize="small" sx={{ color: '#757575' }} />
            <Typography variant="body2" color="text.secondary">
              <strong>Effort:</strong> {issue.effort_hours} hours
            </Typography>
          </Box>
        )}

        {issue.business_impact && (
          <Box sx={{ mt: 1, p: 1, bgcolor: '#ffebee', borderRadius: 1, borderLeft: '4px solid #d32f2f' }}>
            <Typography variant="body2" sx={{ color: '#c62828', fontWeight: 500 }}>
              <strong>💼 Business Impact:</strong> {issue.business_impact}
            </Typography>
          </Box>
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
          <Box sx={{
            mt: 3,
            p: 3,
            borderRadius: 2,
            background: 'linear-gradient(135deg, #f3e5f5 0%, #e1bee7 100%)',
            border: '1px solid #ce93d8'
          }}>
            <Typography variant="h6" sx={{ mb: 2, display: 'flex', alignItems: 'center', gap: 1 }}>
              <DiamondIcon sx={{ color: '#7b1fa2' }} />
              Recommended Improvements
            </Typography>
            <List sx={{ bgcolor: 'rgba(255,255,255,0.6)', borderRadius: 1 }}>
              {recommendations.map((rec, index) => (
                <ListItem key={index} sx={{
                  borderBottom: index < recommendations.length - 1 ? '1px solid #e0e0e0' : 'none',
                  '&:hover': { bgcolor: 'rgba(123, 31, 162, 0.05)' }
                }}>
                  <ListItemIcon>
                    <FlashOnIcon sx={{ color: '#7b1fa2' }} />
                  </ListItemIcon>
                  <ListItemText
                    primary={rec}
                    sx={{ '& .MuiListItemText-primary': { fontWeight: 500 } }}
                  />
                </ListItem>
              ))}
            </List>
          </Box>
        )}

        {/* Raw analysis fallback - try to parse JSON first, then render as markdown */}
        {layerData.raw_analysis && issues.length === 0 && (() => {
          // Try to extract and parse JSON from raw_analysis
          let parsedData = null;
          const rawContent = typeof layerData.raw_analysis === 'string'
            ? layerData.raw_analysis
            : JSON.stringify(layerData.raw_analysis, null, 2);

          try {
            // Try direct JSON parse first
            parsedData = JSON.parse(rawContent);
          } catch {
            // Try to extract JSON from markdown code blocks
            const jsonMatch = rawContent.match(/```(?:json)?\s*\n?([\s\S]*?)\n?```/);
            if (jsonMatch) {
              try {
                parsedData = JSON.parse(jsonMatch[1]);
              } catch (e) {
                console.error('Failed to parse JSON from markdown:', e);
              }
            }
          }

          // If we successfully parsed JSON with expected structure, display it properly
          if (parsedData && (
            parsedData.critical_issues ||
            parsedData.bottlenecks ||
            parsedData.coverage_gaps ||
            parsedData.missing_devops ||
            parsedData.quality_issues ||
            parsedData.recommendations
          )) {
            const parsedIssues = parsedData.critical_issues ||
                                parsedData.bottlenecks ||
                                parsedData.coverage_gaps ||
                                parsedData.missing_devops ||
                                parsedData.quality_issues ||
                                [];
            const parsedRecommendations = parsedData.recommendations || [];

            return (
              <Box>
                {/* Parsed Issues */}
                {parsedIssues.length > 0 && (
                  <Box sx={{ mb: 3 }}>
                    <Typography variant="h6" sx={{ mb: 2 }}>
                      {parsedIssues.length} {layerName === 'security' ? 'Security Issues' :
                        layerName === 'performance' ? 'Performance Bottlenecks' :
                        layerName === 'testing' ? 'Test Coverage Gaps' :
                        layerName === 'devops' ? 'DevOps Gaps' :
                        'Code Quality Issues'}
                    </Typography>
                    {parsedIssues.map((issue, index) => renderIssue(issue, index))}
                  </Box>
                )}

                {/* Parsed Recommendations */}
                {parsedRecommendations.length > 0 && (
                  <Box sx={{
                    mt: 3,
                    p: 3,
                    borderRadius: 2,
                    background: 'linear-gradient(135deg, #f3e5f5 0%, #e1bee7 100%)',
                    border: '1px solid #ce93d8'
                  }}>
                    <Typography variant="h6" sx={{ mb: 2, display: 'flex', alignItems: 'center', gap: 1 }}>
                      <DiamondIcon sx={{ color: '#7b1fa2' }} />
                      Recommended Improvements
                    </Typography>
                    <List sx={{ bgcolor: 'rgba(255,255,255,0.6)', borderRadius: 1 }}>
                      {parsedRecommendations.map((rec, index) => (
                        <ListItem key={index} sx={{
                          borderBottom: index < parsedRecommendations.length - 1 ? '1px solid #e0e0e0' : 'none',
                          '&:hover': { bgcolor: 'rgba(123, 31, 162, 0.05)' }
                        }}>
                          <ListItemIcon>
                            <FlashOnIcon sx={{ color: '#7b1fa2' }} />
                          </ListItemIcon>
                          <ListItemText
                            primary={rec}
                            sx={{ '& .MuiListItemText-primary': { fontWeight: 500 } }}
                          />
                        </ListItem>
                      ))}
                    </List>
                  </Box>
                )}
              </Box>
            );
          }

          // Otherwise, show markdown fallback
          return (
            <Paper sx={{ p: 3, bgcolor: '#f5f5f5' }}>
              <Alert severity="warning" sx={{ mb: 2 }}>
                <Typography variant="body2">
                  <InfoIcon fontSize="small" sx={{ verticalAlign: 'middle', mr: 1 }} />
                  Unable to parse structured analysis. Showing raw AI response:
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
        })()}
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

    // Check if we have structured data
    const hasStructuredData = synthesis.executive_summary ||
                               synthesis.critical_issues?.length > 0 ||
                               synthesis.high_priority?.length > 0 ||
                               synthesis.medium_priority?.length > 0 ||
                               synthesis.low_priority?.length > 0 ||
                               synthesis.quick_wins?.length > 0;

    // If we have structured data, render it directly
    if (hasStructuredData) {
      return renderParsedSynthesis(synthesis);
    }

    // Otherwise, try to parse from raw_analysis or raw content
    let parsedData = null;
    const rawContent = synthesis.raw_analysis ||
                      (typeof synthesis === 'string' ? synthesis : JSON.stringify(synthesis, null, 2));

    // Try to extract and parse JSON from markdown code blocks or raw JSON
    try {
      // Try direct JSON parse first
      parsedData = JSON.parse(rawContent);
    } catch {
      // Try to extract JSON from markdown code blocks
      const jsonMatch = rawContent.match(/```(?:json)?\s*\n?([\s\S]*?)\n?```/);
      if (jsonMatch) {
        try {
          parsedData = JSON.parse(jsonMatch[1]);
        } catch (e) {
          console.error('Failed to parse JSON from markdown:', e);
        }
      }
    }

    // If we successfully parsed JSON with the expected structure, display it properly
    if (parsedData && (parsedData.executive_summary || parsedData.critical_issues || parsedData.high_priority)) {
      return renderParsedSynthesis(parsedData);
    }

    // Otherwise show markdown fallback
    return (
      <Paper sx={{ p: 3 }}>
        <Alert severity="warning" sx={{ mb: 2 }}>
          <Typography variant="body2">
            <InfoIcon fontSize="small" sx={{ verticalAlign: 'middle', mr: 1 }} />
            Unable to parse structured report. Showing raw AI response:
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
  };

  // Helper to render parsed synthesis data
  const renderParsedSynthesis = (data) => {

    return (
      <Box>
        {/* Executive Summary */}
        {data.executive_summary && (
          <Alert severity="info" sx={{ mb: 3 }}>
            <Typography variant="h6" sx={{ mb: 1 }}>Executive Summary</Typography>
            <Typography variant="body1">{data.executive_summary}</Typography>
          </Alert>
        )}

        {/* Quick Wins */}
        {data.quick_wins && data.quick_wins.length > 0 && (
          <Box sx={{
            p: 3,
            mb: 3,
            borderRadius: 2,
            background: 'linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 100%)',
            border: '2px solid #66bb6a',
            boxShadow: '0 4px 12px rgba(76, 175, 80, 0.2)'
          }}>
            <Typography variant="h6" sx={{ mb: 2, display: 'flex', alignItems: 'center', gap: 1 }}>
              <FlashOnIcon sx={{ color: '#2e7d32', fontSize: 28 }} />
              <strong>Quick Wins</strong>
              <Chip
                label="< 4 hours each"
                sx={{
                  ml: 1,
                  background: 'linear-gradient(135deg, #4caf50 0%, #388e3c 100%)',
                  color: 'white',
                  fontWeight: 600
                }}
                size="small"
              />
            </Typography>
            <List sx={{ bgcolor: 'rgba(255,255,255,0.7)', borderRadius: 1 }}>
              {data.quick_wins.map((win, index) => (
                <ListItem key={index} sx={{
                  borderBottom: index < data.quick_wins.length - 1 ? '1px solid #e0e0e0' : 'none',
                  '&:hover': { bgcolor: 'rgba(46, 125, 50, 0.05)' }
                }}>
                  <ListItemIcon>
                    <StarIcon sx={{ color: '#ffc107' }} />
                  </ListItemIcon>
                  <ListItemText
                    primary={win}
                    sx={{ '& .MuiListItemText-primary': { fontWeight: 500 } }}
                  />
                </ListItem>
              ))}
            </List>
          </Box>
        )}

        {/* Critical Issues */}
        {data.critical_issues && data.critical_issues.length > 0 && (
          <Accordion
            expanded={expandedPanel === 'critical'}
            onChange={() => setExpandedPanel(expandedPanel === 'critical' ? false : 'critical')}
            sx={{
              mb: 2,
              borderRadius: '8px !important',
              boxShadow: '0 2px 8px rgba(211, 47, 47, 0.2)',
              '&:before': { display: 'none' }
            }}
          >
            <AccordionSummary
              expandIcon={<ExpandMoreIcon />}
              sx={{
                background: 'linear-gradient(135deg, #ffebee 0%, #ffcdd2 100%)',
                borderRadius: 1,
                '&:hover': { background: 'linear-gradient(135deg, #ffcdd2 0%, #ef9a9a 100%)' }
              }}
            >
              <Box sx={{ display: 'flex', alignItems: 'center', width: '100%', gap: 1 }}>
                <FireIcon sx={{ color: '#d32f2f', fontSize: 28 }} />
                <Typography variant="h6" sx={{ fontWeight: 700 }}>
                  Critical Issues ({data.critical_issues.length})
                </Typography>
                <Chip
                  label="Fix Immediately"
                  sx={{
                    ml: 'auto',
                    background: 'linear-gradient(135deg, #d32f2f 0%, #c62828 100%)',
                    color: 'white',
                    fontWeight: 600
                  }}
                  size="small"
                />
              </Box>
            </AccordionSummary>
            <AccordionDetails sx={{ bgcolor: '#fafafa', p: 3 }}>
              {data.critical_issues.map((issue, index) => renderIssue(issue, index))}
            </AccordionDetails>
          </Accordion>
        )}

        {/* High Priority */}
        {data.high_priority && data.high_priority.length > 0 && (
          <Accordion
            expanded={expandedPanel === 'high'}
            onChange={() => setExpandedPanel(expandedPanel === 'high' ? false : 'high')}
            sx={{
              mb: 2,
              borderRadius: '8px !important',
              boxShadow: '0 2px 8px rgba(245, 124, 0, 0.2)',
              '&:before': { display: 'none' }
            }}
          >
            <AccordionSummary
              expandIcon={<ExpandMoreIcon />}
              sx={{
                background: 'linear-gradient(135deg, #fff3e0 0%, #ffe0b2 100%)',
                borderRadius: 1,
                '&:hover': { background: 'linear-gradient(135deg, #ffe0b2 0%, #ffcc80 100%)' }
              }}
            >
              <Box sx={{ display: 'flex', alignItems: 'center', width: '100%', gap: 1 }}>
                <BoltIcon sx={{ color: '#f57c00', fontSize: 28 }} />
                <Typography variant="h6" sx={{ fontWeight: 700 }}>
                  High Priority ({data.high_priority.length})
                </Typography>
                <Chip
                  label="1-2 Sprints"
                  sx={{
                    ml: 'auto',
                    background: 'linear-gradient(135deg, #f57c00 0%, #e65100 100%)',
                    color: 'white',
                    fontWeight: 600
                  }}
                  size="small"
                />
              </Box>
            </AccordionSummary>
            <AccordionDetails sx={{ bgcolor: '#fafafa', p: 3 }}>
              {data.high_priority.map((issue, index) => renderIssue(issue, index))}
            </AccordionDetails>
          </Accordion>
        )}

        {/* Medium Priority */}
        {data.medium_priority && data.medium_priority.length > 0 && (
          <Accordion
            expanded={expandedPanel === 'medium'}
            onChange={() => setExpandedPanel(expandedPanel === 'medium' ? false : 'medium')}
            sx={{
              mb: 2,
              borderRadius: '8px !important',
              boxShadow: '0 2px 8px rgba(25, 118, 210, 0.2)',
              '&:before': { display: 'none' }
            }}
          >
            <AccordionSummary
              expandIcon={<ExpandMoreIcon />}
              sx={{
                background: 'linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%)',
                borderRadius: 1,
                '&:hover': { background: 'linear-gradient(135deg, #bbdefb 0%, #90caf9 100%)' }
              }}
            >
              <Box sx={{ display: 'flex', alignItems: 'center', width: '100%', gap: 1 }}>
                <StarIcon sx={{ color: '#1976d2', fontSize: 28 }} />
                <Typography variant="h6" sx={{ fontWeight: 700 }}>
                  Medium Priority ({data.medium_priority.length})
                </Typography>
                <Chip
                  label="1-2 Months"
                  sx={{
                    ml: 'auto',
                    background: 'linear-gradient(135deg, #1976d2 0%, #0d47a1 100%)',
                    color: 'white',
                    fontWeight: 600
                  }}
                  size="small"
                />
              </Box>
            </AccordionSummary>
            <AccordionDetails sx={{ bgcolor: '#fafafa', p: 3 }}>
              {data.medium_priority.map((issue, index) => renderIssue(issue, index))}
            </AccordionDetails>
          </Accordion>
        )}

        {/* Low Priority */}
        {data.low_priority && data.low_priority.length > 0 && (
          <Accordion
            expanded={expandedPanel === 'low'}
            onChange={() => setExpandedPanel(expandedPanel === 'low' ? false : 'low')}
            sx={{
              mb: 2,
              borderRadius: '8px !important',
              boxShadow: '0 2px 8px rgba(56, 142, 60, 0.2)',
              '&:before': { display: 'none' }
            }}
          >
            <AccordionSummary
              expandIcon={<ExpandMoreIcon />}
              sx={{
                background: 'linear-gradient(135deg, #f1f8e9 0%, #dcedc8 100%)',
                borderRadius: 1,
                '&:hover': { background: 'linear-gradient(135deg, #dcedc8 0%, #c5e1a5 100%)' }
              }}
            >
              <Box sx={{ display: 'flex', alignItems: 'center', width: '100%', gap: 1 }}>
                <TrophyIcon sx={{ color: '#388e3c', fontSize: 28 }} />
                <Typography variant="h6" sx={{ fontWeight: 700 }}>
                  Low Priority ({data.low_priority.length})
                </Typography>
                <Chip
                  label="Nice to Have"
                  sx={{
                    ml: 'auto',
                    background: 'linear-gradient(135deg, #388e3c 0%, #2e7d32 100%)',
                    color: 'white',
                    fontWeight: 600
                  }}
                  size="small"
                />
              </Box>
            </AccordionSummary>
            <AccordionDetails sx={{ bgcolor: '#fafafa', p: 3 }}>
              {data.low_priority.map((issue, index) => renderIssue(issue, index))}
            </AccordionDetails>
          </Accordion>
        )}

        {/* Effort Estimate */}
        {data.estimated_total_effort_days && (
          <Alert severity="info" sx={{ mt: 3 }}>
            <Typography variant="body1">
              <strong>Estimated Total Effort:</strong> {data.estimated_total_effort_days} days
            </Typography>
          </Alert>
        )}
      </Box>
    );
  };

  return (
    <Box sx={{ width: '100%' }}>
      {/* Premium Feature Banner */}
      <Box sx={{
        mb: 3,
        p: 3,
        borderRadius: 2,
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        color: 'white',
        boxShadow: '0 4px 20px rgba(102, 126, 234, 0.3)',
        position: 'relative',
        overflow: 'hidden',
        '&::before': {
          content: '""',
          position: 'absolute',
          top: 0,
          right: 0,
          width: '200px',
          height: '200px',
          background: 'radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%)',
          borderRadius: '50%',
          transform: 'translate(50%, -50%)'
        }
      }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, position: 'relative' }}>
          <ScienceIcon sx={{ fontSize: 48 }} />
          <Box>
            <Typography variant="h5" sx={{ fontWeight: 700, mb: 0.5 }}>
              Multi-Stage Deep Analysis Complete! ✨
            </Typography>
            <Typography variant="body1" sx={{ opacity: 0.95 }}>
              Premium analysis examined 5 architectural layers with AI-powered insights
            </Typography>
          </Box>
        </Box>
      </Box>

      {/* Tab Navigation */}
      <Paper sx={{
        width: '100%',
        mb: 2,
        borderRadius: 2,
        overflow: 'hidden',
        boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
      }}>
        <Tabs
          value={activeTab}
          onChange={(e, newValue) => setActiveTab(newValue)}
          variant="scrollable"
          scrollButtons="auto"
          sx={{
            '& .MuiTab-root': {
              fontWeight: 600,
              minHeight: 64,
              '&.Mui-selected': {
                background: 'linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%)',
              }
            },
            '& .MuiTabs-indicator': {
              height: 3,
              background: 'linear-gradient(90deg, #667eea 0%, #764ba2 100%)',
            }
          }}
        >
          <Tab
            label="Synthesis Report"
            icon={<TrendingUpIcon />}
            iconPosition="start"
            sx={{ gap: 1 }}
          />
          <Tab
            label="Security"
            icon={<ShieldIcon />}
            iconPosition="start"
            sx={{ gap: 1 }}
          />
          <Tab
            label="Performance"
            icon={<BoltIcon />}
            iconPosition="start"
            sx={{ gap: 1 }}
          />
          <Tab
            label="Testing"
            icon={<ScienceIcon />}
            iconPosition="start"
            sx={{ gap: 1 }}
          />
          <Tab
            label="DevOps"
            icon={<RocketIcon />}
            iconPosition="start"
            sx={{ gap: 1 }}
          />
          <Tab
            label="Code Quality"
            icon={<DiamondIcon />}
            iconPosition="start"
            sx={{ gap: 1 }}
          />
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
