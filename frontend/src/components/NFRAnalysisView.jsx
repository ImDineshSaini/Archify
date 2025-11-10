import { useState } from 'react';
import {
  Box,
  Paper,
  Typography,
  Grid,
  Card,
  CardContent,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Chip,
  LinearProgress,
  Alert,
  Divider,
  List,
  ListItem,
  ListItemText,
  Tooltip,
} from '@mui/material';
import {
  ExpandMore,
  TrendingUp,
  TrendingDown,
  CheckCircle,
  Warning,
  Error as ErrorIcon,
  Speed,
  Security,
  Build,
  BarChart as BarChartIcon,
  Storage,
  Cloud,
  Accessible,
  AccountTree,
} from '@mui/icons-material';
import {
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
  ResponsiveContainer,
  Tooltip as RechartsTooltip,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Cell,
} from 'recharts';

const NFRAnalysisView = ({ nfrAnalysis }) => {
  const [expandedCategory, setExpandedCategory] = useState(null);

  if (!nfrAnalysis || !nfrAnalysis.nfr_scores) {
    return (
      <Alert severity="info">
        NFR (Non-Functional Requirements) analysis not available for this analysis.
      </Alert>
    );
  }

  const { nfr_scores, nfr_categories, category_averages, recommendations } = nfrAnalysis;

  const getScoreColor = (score) => {
    if (score >= 80) return '#4caf50';
    if (score >= 60) return '#ff9800';
    return '#f44336';
  };

  const getScoreIcon = (score) => {
    if (score >= 80) return <CheckCircle sx={{ color: '#4caf50' }} />;
    if (score >= 60) return <Warning sx={{ color: '#ff9800' }} />;
    return <ErrorIcon sx={{ color: '#f44336' }} />;
  };

  const getCategoryIcon = (category) => {
    const iconMap = {
      'Performance & Scale': <Speed />,
      'Reliability & Resilience': <CheckCircle />,
      'Security & Compliance': <Security />,
      'Maintainability & Operations': <Build />,
      'User Experience': <Accessible />,
      'Integration & Portability': <AccountTree />,
      'Efficiency': <BarChartIcon />,
      'Business Continuity': <Cloud />,
    };
    return iconMap[category] || <Storage />;
  };

  // Prepare radar chart data
  const radarData = Object.entries(category_averages || {}).map(([category, score]) => ({
    category: category.replace(' & ', '\n'),
    score: Math.round(score),
    fullMark: 100,
  }));

  // Prepare bar chart data for all NFRs
  const top10NFRs = Object.entries(nfr_scores)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 10)
    .map(([name, score]) => ({
      name: name.replace(/_/g, ' ').replace(/\b\w/g, (l) => l.toUpperCase()),
      score: Math.round(score),
    }));

  const bottom10NFRs = Object.entries(nfr_scores)
    .sort((a, b) => a[1] - b[1])
    .slice(0, 10)
    .map(([name, score]) => ({
      name: name.replace(/_/g, ' ').replace(/\b\w/g, (l) => l.toUpperCase()),
      score: Math.round(score),
    }));

  return (
    <Box>
      {/* Header */}
      <Typography variant="h5" gutterBottom sx={{ mb: 3 }}>
        📊 Comprehensive NFR Analysis (40+ Quality Attributes)
      </Typography>

      <Alert severity="info" sx={{ mb: 3 }}>
        <Typography variant="body2">
          <strong>What makes this different from SonarQube?</strong>
          <br />
          SonarQube focuses on code-level issues (bugs, code smells, security vulnerabilities).
          <br />
          <strong>Archify analyzes architecture-level quality</strong> - evaluating 40+ Non-Functional Requirements
          that impact business outcomes: scalability, reliability, cost efficiency, and more.
        </Typography>
      </Alert>

      {/* Category Overview Cards */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        {Object.entries(category_averages || {}).map(([category, score]) => (
          <Grid item xs={12} sm={6} md={3} key={category}>
            <Card
              sx={{
                background: `linear-gradient(135deg, ${getScoreColor(score)}22 0%, ${getScoreColor(score)}44 100%)`,
                border: `2px solid ${getScoreColor(score)}`,
              }}
            >
              <CardContent>
                <Box display="flex" alignItems="center" mb={1}>
                  <Box sx={{ color: getScoreColor(score), mr: 1 }}>
                    {getCategoryIcon(category)}
                  </Box>
                  <Typography variant="h6" fontSize="0.9rem">
                    {category}
                  </Typography>
                </Box>
                <Typography variant="h3" color={getScoreColor(score)}>
                  {Math.round(score)}
                </Typography>
                <LinearProgress
                  variant="determinate"
                  value={score}
                  sx={{
                    mt: 1,
                    height: 8,
                    borderRadius: 4,
                    backgroundColor: '#e0e0e0',
                    '& .MuiLinearProgress-bar': {
                      backgroundColor: getScoreColor(score),
                    },
                  }}
                />
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      {/* Radar Chart - Category Overview */}
      <Paper sx={{ p: 3, mb: 4 }}>
        <Typography variant="h6" gutterBottom>
          Quality Categories Radar
        </Typography>
        <ResponsiveContainer width="100%" height={400}>
          <RadarChart data={radarData}>
            <PolarGrid />
            <PolarAngleAxis dataKey="category" />
            <PolarRadiusAxis angle={90} domain={[0, 100]} />
            <Radar
              name="Score"
              dataKey="score"
              stroke="#8884d8"
              fill="#8884d8"
              fillOpacity={0.6}
            />
            <RechartsTooltip />
          </RadarChart>
        </ResponsiveContainer>
      </Paper>

      {/* Top 10 Strengths */}
      <Paper sx={{ p: 3, mb: 4 }}>
        <Typography variant="h6" gutterBottom>
          ✅ Top 10 Strengths
        </Typography>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={top10NFRs} layout="vertical">
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis type="number" domain={[0, 100]} />
            <YAxis dataKey="name" type="category" width={150} />
            <RechartsTooltip />
            <Bar dataKey="score">
              {top10NFRs.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={getScoreColor(entry.score)} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </Paper>

      {/* Top 10 Weaknesses */}
      <Paper sx={{ p: 3, mb: 4 }}>
        <Typography variant="h6" gutterBottom>
          ⚠️ Top 10 Areas for Improvement
        </Typography>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={bottom10NFRs} layout="vertical">
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis type="number" domain={[0, 100]} />
            <YAxis dataKey="name" type="category" width={150} />
            <RechartsTooltip />
            <Bar dataKey="score">
              {bottom10NFRs.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={getScoreColor(entry.score)} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </Paper>

      {/* Detailed NFR Breakdown by Category */}
      <Typography variant="h6" gutterBottom sx={{ mt: 4, mb: 2 }}>
        📋 Detailed NFR Breakdown (All 40+ Attributes)
      </Typography>

      {Object.entries(nfr_categories || {}).map(([category, attributes]) => {
        const categoryScore = category_averages[category] || 0;

        return (
          <Accordion
            key={category}
            expanded={expandedCategory === category}
            onChange={() => setExpandedCategory(expandedCategory === category ? null : category)}
            sx={{ mb: 2 }}
          >
            <AccordionSummary expandIcon={<ExpandMore />}>
              <Box display="flex" alignItems="center" width="100%">
                <Box sx={{ color: getScoreColor(categoryScore), mr: 2 }}>
                  {getCategoryIcon(category)}
                </Box>
                <Typography variant="h6" sx={{ flexGrow: 1 }}>
                  {category}
                </Typography>
                <Chip
                  label={`${Math.round(categoryScore)}/100`}
                  sx={{
                    bgcolor: getScoreColor(categoryScore),
                    color: 'white',
                    fontWeight: 'bold',
                    mr: 2,
                  }}
                />
                {getScoreIcon(categoryScore)}
              </Box>
            </AccordionSummary>
            <AccordionDetails>
              <Grid container spacing={2}>
                {attributes.map((attr) => {
                  const score = nfr_scores[attr] || 0;
                  return (
                    <Grid item xs={12} sm={6} md={4} key={attr}>
                      <Card variant="outlined">
                        <CardContent>
                          <Box display="flex" justifyContent="space-between" alignItems="center" mb={1}>
                            <Typography variant="subtitle2" fontWeight="bold">
                              {attr.replace(/_/g, ' ').replace(/\b\w/g, (l) => l.toUpperCase())}
                            </Typography>
                            {getScoreIcon(score)}
                          </Box>
                          <Typography variant="h4" color={getScoreColor(score)}>
                            {Math.round(score)}
                          </Typography>
                          <LinearProgress
                            variant="determinate"
                            value={score}
                            sx={{
                              mt: 1,
                              height: 6,
                              borderRadius: 3,
                              backgroundColor: '#e0e0e0',
                              '& .MuiLinearProgress-bar': {
                                backgroundColor: getScoreColor(score),
                              },
                            }}
                          />
                        </CardContent>
                      </Card>
                    </Grid>
                  );
                })}
              </Grid>
            </AccordionDetails>
          </Accordion>
        );
      })}

      {/* Priority Recommendations */}
      {recommendations && recommendations.length > 0 && (
        <Paper sx={{ p: 3, mt: 4 }}>
          <Typography variant="h6" gutterBottom>
            🎯 Priority Recommendations
          </Typography>
          <Divider sx={{ mb: 2 }} />
          <List>
            {recommendations.map((rec, index) => (
              <ListItem
                key={index}
                sx={{
                  border: `1px solid ${rec.priority === 'HIGH' ? '#f44336' : rec.priority === 'MEDIUM' ? '#ff9800' : '#2196f3'}`,
                  borderRadius: 1,
                  mb: 2,
                  flexDirection: 'column',
                  alignItems: 'flex-start',
                }}
              >
                <Box display="flex" alignItems="center" width="100%" mb={1}>
                  <Chip
                    label={rec.priority}
                    color={rec.priority === 'HIGH' ? 'error' : rec.priority === 'MEDIUM' ? 'warning' : 'info'}
                    size="small"
                    sx={{ mr: 2, fontWeight: 'bold' }}
                  />
                  <Typography variant="subtitle1" fontWeight="bold" sx={{ flexGrow: 1 }}>
                    {rec.attribute}
                  </Typography>
                  <Chip
                    label={`${rec.current_score}/100`}
                    size="small"
                    sx={{
                      bgcolor: getScoreColor(rec.current_score),
                      color: 'white',
                    }}
                  />
                </Box>
                <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                  <strong>Business Impact:</strong> {rec.impact}
                </Typography>
                <Typography variant="body2">
                  <strong>Recommendation:</strong> {rec.recommendation}
                </Typography>
              </ListItem>
            ))}
          </List>
        </Paper>
      )}
    </Box>
  );
};

export default NFRAnalysisView;
