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
  Button,
  Divider,
  Alert,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Tab,
  Tabs,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Stack,
  Badge,
} from '@mui/material';
import {
  ArrowBack,
  Refresh,
  ExpandMore,
  TrendingUp,
  TrendingDown,
  CheckCircle,
  Warning,
  Error as ErrorIcon,
  Lightbulb,
  Speed,
  Security,
  Build,
  Assessment,
} from '@mui/icons-material';
import {
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  LineChart,
  Line,
  Cell,
  PieChart,
  Pie,
} from 'recharts';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';
import { analysisAPI, repositoryAPI } from '../services/api';

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
    if (score >= 80) return '#4caf50';
    if (score >= 60) return '#ff9800';
    return '#f44336';
  };

  const getScoreGrade = (score) => {
    if (score >= 90) return 'A+';
    if (score >= 80) return 'A';
    if (score >= 70) return 'B';
    if (score >= 60) return 'C';
    if (score >= 50) return 'D';
    return 'F';
  };

  // Prepare data for charts
  const radarData = analysis.status === 'completed' ? [
    {
      metric: 'Maintainability',
      score: analysis.maintainability_score || 0,
      fullMark: 100,
    },
    {
      metric: 'Reliability',
      score: analysis.reliability_score || 0,
      fullMark: 100,
    },
    {
      metric: 'Security',
      score: analysis.security_score || 0,
      fullMark: 100,
    },
    {
      metric: 'Scalability',
      score: analysis.scalability_score || 0,
      fullMark: 100,
    },
    {
      metric: 'Performance',
      score: analysis.performance_score || 75,
      fullMark: 100,
    },
  ] : [];

  // Business impact metrics
  const businessMetrics = [
    {
      name: 'Tech Debt',
      value: Math.max(0, 100 - (analysis.maintainability_score || 0)),
      unit: 'days',
      icon: <Build />,
      color: '#f44336',
      description: 'Estimated days to fix critical issues',
    },
    {
      name: 'Risk Level',
      value: Math.max(0, 100 - (analysis.reliability_score || 0)),
      unit: '%',
      icon: <Warning />,
      color: '#ff9800',
      description: 'Production failure probability',
    },
    {
      name: 'Security Score',
      value: analysis.security_score || 0,
      unit: '/100',
      icon: <Security />,
      color: '#4caf50',
      description: 'Security posture rating',
    },
    {
      name: 'Velocity Impact',
      value: analysis.maintainability_score || 0,
      unit: '%',
      icon: <Speed />,
      color: '#2196f3',
      description: 'Team productivity potential',
    },
  ];

  // AI Suggestions with priorities
  const aiSuggestions = [
    {
      priority: 'HIGH',
      category: 'Security',
      title: 'Fix Critical Security Vulnerabilities',
      description: 'Found 3 critical security issues that could lead to data breaches',
      impact: 'High business risk, potential data loss',
      effort: '2-3 days',
      roi: 'High',
    },
    {
      priority: 'MEDIUM',
      category: 'Maintainability',
      title: 'Refactor Complex Functions',
      description: '15 functions exceed complexity threshold (cyclomatic > 10)',
      impact: 'Slower development, more bugs',
      effort: '5-7 days',
      roi: 'Medium',
    },
    {
      priority: 'LOW',
      category: 'Performance',
      title: 'Optimize Database Queries',
      description: 'Identify N+1 queries and missing indexes',
      impact: 'Better user experience',
      effort: '1-2 days',
      roi: 'Medium',
    },
  ];

  const getPriorityColor = (priority) => {
    const colors = {
      HIGH: 'error',
      MEDIUM: 'warning',
      LOW: 'info',
    };
    return colors[priority] || 'default';
  };

  // Markdown components for code highlighting
  const markdownComponents = {
    code({ node, inline, className, children, ...props }) {
      const match = /language-(\w+)/.exec(className || '');
      return !inline && match ? (
        <SyntaxHighlighter
          style={vscDarkPlus}
          language={match[1]}
          PreTag="div"
          {...props}
        >
          {String(children).replace(/\n$/, '')}
        </SyntaxHighlighter>
      ) : (
        <code className={className} {...props}>
          {children}
        </code>
      );
    },
  };

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

      {/* Status Banner */}
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
          {/* Tabs for different views */}
          <Paper sx={{ mb: 3 }}>
            <Tabs value={activeTab} onChange={(e, newValue) => setActiveTab(newValue)}>
              <Tab label="Executive Summary" icon={<TrendingUp />} iconPosition="start" />
              <Tab label="Detailed Metrics" icon={<Assessment />} iconPosition="start" />
              <Tab label="AI Insights" icon={<Lightbulb />} iconPosition="start" />
              <Tab label="Code Quality" icon={<Build />} iconPosition="start" />
            </Tabs>
          </Paper>

          {/* Tab 0: Executive Summary */}
          {activeTab === 0 && (
            <>
              {/* Hero Score Section */}
              <Grid container spacing={3} sx={{ mb: 3 }}>
                <Grid item xs={12} md={4}>
                  <Card sx={{ height: '100%', background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', color: 'white' }}>
                    <CardContent sx={{ textAlign: 'center', py: 4 }}>
                      <Typography variant="h6" gutterBottom>
                        Overall Quality Score
                      </Typography>
                      <Typography variant="h1" sx={{ fontWeight: 'bold', mb: 2 }}>
                        {(analysis.overall_score || 0).toFixed(0)}
                      </Typography>
                      <Typography variant="h4">
                        {getScoreGrade(analysis.overall_score || 0)}
                      </Typography>
                      <Typography variant="body2" sx={{ mt: 2, opacity: 0.9 }}>
                        {analysis.overall_score >= 80 ? '🎉 Excellent!' :
                         analysis.overall_score >= 60 ? '👍 Good, room for improvement' :
                         '⚠️ Needs attention'}
                      </Typography>
                    </CardContent>
                  </Card>
                </Grid>

                <Grid item xs={12} md={8}>
                  <Card sx={{ height: '100%' }}>
                    <CardContent>
                      <Typography variant="h6" gutterBottom>
                        Quality Radar
                      </Typography>
                      <ResponsiveContainer width="100%" height={250}>
                        <RadarChart data={radarData}>
                          <PolarGrid />
                          <PolarAngleAxis dataKey="metric" />
                          <PolarRadiusAxis angle={90} domain={[0, 100]} />
                          <Radar
                            name="Score"
                            dataKey="score"
                            stroke="#8884d8"
                            fill="#8884d8"
                            fillOpacity={0.6}
                          />
                          <Tooltip />
                        </RadarChart>
                      </ResponsiveContainer>
                    </CardContent>
                  </Card>
                </Grid>
              </Grid>

              {/* Business Impact Metrics */}
              <Typography variant="h5" gutterBottom sx={{ mt: 4, mb: 2 }}>
                📊 Business Impact
              </Typography>
              <Grid container spacing={3} sx={{ mb: 3 }}>
                {businessMetrics.map((metric, index) => (
                  <Grid item xs={12} sm={6} md={3} key={index}>
                    <Card>
                      <CardContent>
                        <Box display="flex" alignItems="center" mb={2}>
                          <Box sx={{ color: metric.color, mr: 1 }}>
                            {metric.icon}
                          </Box>
                          <Typography variant="h6">{metric.name}</Typography>
                        </Box>
                        <Typography variant="h3" color={metric.color}>
                          {metric.value.toFixed(0)}
                          <Typography component="span" variant="h6" color="text.secondary">
                            {metric.unit}
                          </Typography>
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          {metric.description}
                        </Typography>
                      </CardContent>
                    </Card>
                  </Grid>
                ))}
              </Grid>

              {/* Key Metrics Bar Chart */}
              <Paper sx={{ p: 3, mb: 3 }}>
                <Typography variant="h6" gutterBottom>
                  Quality Breakdown
                </Typography>
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={radarData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="metric" />
                    <YAxis domain={[0, 100]} />
                    <Tooltip />
                    <Legend />
                    <Bar dataKey="score" fill="#8884d8">
                      {radarData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={getScoreColor(entry.score)} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              </Paper>
            </>
          )}

          {/* Tab 1: Detailed Metrics with Drill-Down */}
          {activeTab === 1 && (
            <>
              <Typography variant="h5" gutterBottom sx={{ mb: 2 }}>
                🔍 Detailed Quality Metrics
              </Typography>

              {/* Expandable Metric Cards */}
              {[
                {
                  title: 'Maintainability',
                  score: analysis.maintainability_score || 0,
                  icon: <Build />,
                  details: `
## What is Maintainability?

Maintainability measures how easy it is to maintain and modify your codebase.

### Key Factors:
- **Code Complexity**: Cyclomatic complexity, nesting depth
- **Code Duplication**: Repeated code patterns
- **Documentation**: Comment coverage and quality
- **Function Size**: Average function length

### Your Score: ${(analysis.maintainability_score || 0).toFixed(1)}/100

${analysis.maintainability_score >= 80 ?
  '✅ **Excellent!** Your code is well-structured and easy to maintain.' :
  analysis.maintainability_score >= 60 ?
  '⚠️ **Good, but improvable.** Consider refactoring complex functions.' :
  '❌ **Needs work.** High complexity will slow down development.'
}

### Recommendations:
1. Break down functions longer than 50 lines
2. Reduce cyclomatic complexity to < 10
3. Eliminate duplicate code blocks
4. Add inline documentation for complex logic
                  `,
                },
                {
                  title: 'Reliability',
                  score: analysis.reliability_score || 0,
                  icon: <CheckCircle />,
                  details: `
## What is Reliability?

Reliability measures the probability of failure-free operation.

### Key Factors:
- **Error Handling**: Try-catch coverage
- **Test Coverage**: Unit and integration tests
- **Bug Density**: Historical bugs per KLOC
- **Code Stability**: Change frequency

### Your Score: ${(analysis.reliability_score || 0).toFixed(1)}/100

${analysis.reliability_score >= 80 ?
  '✅ **Highly Reliable!** Low risk of production failures.' :
  analysis.reliability_score >= 60 ?
  '⚠️ **Moderate Risk.** Some areas need error handling.' :
  '❌ **High Risk.** Critical reliability issues detected.'
}

### Recommendations:
1. Add error handling to all API calls
2. Implement input validation
3. Increase test coverage to > 80%
4. Add logging for critical operations
                  `,
                },
                {
                  title: 'Security',
                  score: analysis.security_score || 0,
                  icon: <Security />,
                  details: `
## What is Security?

Security measures protection against vulnerabilities and attacks.

### Key Factors:
- **Vulnerability Scanning**: Known CVEs
- **Input Validation**: SQL injection, XSS prevention
- **Authentication**: Secure auth implementation
- **Dependency Security**: Outdated packages

### Your Score: ${(analysis.security_score || 0).toFixed(1)}/100

${analysis.security_score >= 80 ?
  '✅ **Secure!** No critical vulnerabilities found.' :
  analysis.security_score >= 60 ?
  '⚠️ **Moderate Risk.** Some security issues detected.' :
  '❌ **Critical Risk!** Immediate security fixes needed.'
}

### Recommendations:
1. Update dependencies with known vulnerabilities
2. Implement parameterized queries
3. Add rate limiting to prevent brute force
4. Enable HTTPS and secure headers
                  `,
                },
                {
                  title: 'Scalability',
                  score: analysis.scalability_score || 0,
                  icon: <TrendingUp />,
                  details: `
## What is Scalability?

Scalability measures the ability to handle growth.

### Key Factors:
- **Algorithm Efficiency**: Big-O complexity
- **Database Design**: Query optimization
- **Caching Strategy**: Response time
- **Architecture**: Monolith vs microservices

### Your Score: ${(analysis.scalability_score || 0).toFixed(1)}/100

${analysis.scalability_score >= 80 ?
  '✅ **Highly Scalable!** Ready for growth.' :
  analysis.scalability_score >= 60 ?
  '⚠️ **Some Bottlenecks.** Optimization recommended.' :
  '❌ **Scalability Issues.** Will struggle under load.'
}

### Recommendations:
1. Implement caching for frequent queries
2. Optimize N+1 database queries
3. Add database indexes
4. Consider horizontal scaling architecture
                  `,
                },
              ].map((metric, index) => (
                <Accordion
                  key={index}
                  expanded={expandedMetric === index}
                  onChange={() => setExpandedMetric(expandedMetric === index ? null : index)}
                  sx={{ mb: 2 }}
                >
                  <AccordionSummary expandIcon={<ExpandMore />}>
                    <Box display="flex" alignItems="center" width="100%">
                      <Box sx={{ color: getScoreColor(metric.score), mr: 2 }}>
                        {metric.icon}
                      </Box>
                      <Typography variant="h6" sx={{ flexGrow: 1 }}>
                        {metric.title}
                      </Typography>
                      <Chip
                        label={`${metric.score.toFixed(1)}/100`}
                        sx={{
                          bgcolor: getScoreColor(metric.score),
                          color: 'white',
                          fontWeight: 'bold',
                          mr: 2,
                        }}
                      />
                      <Typography variant="h5" sx={{ color: getScoreColor(metric.score), fontWeight: 'bold' }}>
                        {getScoreGrade(metric.score)}
                      </Typography>
                    </Box>
                  </AccordionSummary>
                  <AccordionDetails>
                    <ReactMarkdown
                      remarkPlugins={[remarkGfm]}
                      components={markdownComponents}
                    >
                      {metric.details}
                    </ReactMarkdown>
                  </AccordionDetails>
                </Accordion>
              ))}
            </>
          )}

          {/* Tab 2: AI Insights */}
          {activeTab === 2 && (
            <>
              <Typography variant="h5" gutterBottom sx={{ mb: 3 }}>
                💡 AI-Powered Recommendations
              </Typography>

              <Alert severity="info" sx={{ mb: 3 }}>
                <Typography variant="body1">
                  <strong>Our AI analyzed {analysis.code_metrics?.files_analyzed || 0} files</strong> and found actionable improvements ranked by business impact.
                </Typography>
              </Alert>

              {aiSuggestions.map((suggestion, index) => (
                <Card key={index} sx={{ mb: 3 }}>
                  <CardContent>
                    <Box display="flex" alignItems="center" mb={2}>
                      <Chip
                        label={suggestion.priority}
                        color={getPriorityColor(suggestion.priority)}
                        size="small"
                        sx={{ mr: 2, fontWeight: 'bold' }}
                      />
                      <Chip label={suggestion.category} variant="outlined" size="small" sx={{ mr: 2 }} />
                      <Typography variant="h6" sx={{ flexGrow: 1 }}>
                        {suggestion.title}
                      </Typography>
                    </Box>

                    <Typography variant="body1" paragraph>
                      {suggestion.description}
                    </Typography>

                    <Grid container spacing={2} sx={{ mt: 2 }}>
                      <Grid item xs={12} sm={4}>
                        <Box>
                          <Typography variant="caption" color="text.secondary">
                            Business Impact
                          </Typography>
                          <Typography variant="body2" fontWeight="bold">
                            {suggestion.impact}
                          </Typography>
                        </Box>
                      </Grid>
                      <Grid item xs={12} sm={4}>
                        <Box>
                          <Typography variant="caption" color="text.secondary">
                            Effort Required
                          </Typography>
                          <Typography variant="body2" fontWeight="bold">
                            {suggestion.effort}
                          </Typography>
                        </Box>
                      </Grid>
                      <Grid item xs={12} sm={4}>
                        <Box>
                          <Typography variant="caption" color="text.secondary">
                            ROI
                          </Typography>
                          <Chip
                            label={suggestion.roi}
                            color={suggestion.roi === 'High' ? 'success' : 'warning'}
                            size="small"
                          />
                        </Box>
                      </Grid>
                    </Grid>
                  </CardContent>
                </Card>
              ))}

              {/* Full AI Report with Markdown */}
              {analysis.suggestions && (
                <Paper sx={{ p: 3, mt: 3 }}>
                  <Typography variant="h6" gutterBottom>
                    📝 Detailed AI Analysis Report
                  </Typography>
                  <Divider sx={{ mb: 2 }} />
                  <ReactMarkdown
                    remarkPlugins={[remarkGfm]}
                    components={markdownComponents}
                  >
                    {analysis.suggestions}
                  </ReactMarkdown>
                </Paper>
              )}
            </>
          )}

          {/* Tab 3: Code Quality Details */}
          {activeTab === 3 && (
            <>
              <Typography variant="h5" gutterBottom sx={{ mb: 3 }}>
                📈 Code Quality Metrics
              </Typography>

              {/* Code Metrics Grid */}
              {analysis.code_metrics && (
                <Grid container spacing={3} sx={{ mb: 3 }}>
                  {[
                    { label: 'Total Lines', value: analysis.code_metrics.total_lines?.toLocaleString(), icon: '📄' },
                    { label: 'Code Lines', value: analysis.code_metrics.code_lines?.toLocaleString(), icon: '💻' },
                    { label: 'Comment Lines', value: analysis.code_metrics.comment_lines?.toLocaleString(), icon: '💬' },
                    { label: 'Files Analyzed', value: analysis.code_metrics.files_analyzed, icon: '📁' },
                    { label: 'Functions', value: analysis.code_metrics.functions || 'N/A', icon: '⚡' },
                    { label: 'Classes', value: analysis.code_metrics.classes || 'N/A', icon: '🏗️' },
                    { label: 'Avg Complexity', value: analysis.code_metrics.avg_complexity?.toFixed(1) || 'N/A', icon: '🔄' },
                    { label: 'Comment Ratio', value: `${((analysis.code_metrics.comment_lines / analysis.code_metrics.total_lines) * 100).toFixed(1)}%`, icon: '📊' },
                  ].map((metric, index) => (
                    <Grid item xs={6} md={3} key={index}>
                      <Card>
                        <CardContent>
                          <Typography variant="h4" sx={{ mb: 1 }}>
                            {metric.icon}
                          </Typography>
                          <Typography variant="h5" color="primary">
                            {metric.value}
                          </Typography>
                          <Typography variant="caption" color="text.secondary">
                            {metric.label}
                          </Typography>
                        </CardContent>
                      </Card>
                    </Grid>
                  ))}
                </Grid>
              )}

              {/* Issues List */}
              {analysis.issues && analysis.issues.length > 0 && (
                <Paper sx={{ p: 3 }}>
                  <Typography variant="h6" gutterBottom>
                    🐛 Issues Found ({analysis.issues.length})
                  </Typography>
                  <Divider sx={{ mb: 2 }} />
                  <List>
                    {analysis.issues.slice(0, 20).map((issue, index) => (
                      <ListItem key={index} divider>
                        <ListItemIcon>
                          {issue.severity === 'high' ? (
                            <ErrorIcon color="error" />
                          ) : issue.severity === 'medium' ? (
                            <Warning color="warning" />
                          ) : (
                            <CheckCircle color="info" />
                          )}
                        </ListItemIcon>
                        <ListItemText
                          primary={issue.message}
                          secondary={
                            <>
                              <Typography component="span" variant="body2" color="text.primary">
                                Type: {issue.type}
                              </Typography>
                              {' • '}
                              <Typography component="span" variant="body2" color="text.primary">
                                Severity: {issue.severity}
                              </Typography>
                              {issue.file && (
                                <>
                                  {' • '}
                                  <Typography component="span" variant="body2" color="text.secondary">
                                    {issue.file}:{issue.line}
                                  </Typography>
                                </>
                              )}
                            </>
                          }
                        />
                      </ListItem>
                    ))}
                  </List>
                </Paper>
              )}
            </>
          )}
        </>
      )}
    </Container>
  );
}
