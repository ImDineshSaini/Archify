import {
  Typography,
  Box,
  Paper,
  Grid,
  Card,
  CardContent,
  Tooltip,
} from '@mui/material';
import {
  Warning,
  Security,
  Build,
  Speed,
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
  Tooltip as RechartsTooltip,
  Legend,
  ResponsiveContainer,
  Cell,
} from 'recharts';
import ScoreCard from './ScoreCard';
import { getScoreColor, getScoreGrade } from '../../utils/statusColors';

/**
 * Executive Summary tab (tab 0) – hero score, radar chart, business
 * impact metric cards, and quality breakdown bar chart.
 */
export default function ExecutiveSummaryTab({ analysis }) {
  // Prepare radar data
  const radarData = [
    { metric: 'Maintainability', score: analysis.maintainability_score || 0, fullMark: 100 },
    { metric: 'Reliability', score: analysis.reliability_score || 0, fullMark: 100 },
    { metric: 'Security', score: analysis.security_score || 0, fullMark: 100 },
    { metric: 'Scalability', score: analysis.scalability_score || 0, fullMark: 100 },
    { metric: 'Performance', score: analysis.performance_score || 75, fullMark: 100 },
  ];

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

  const overallScore = analysis.overall_score || 0;

  const scoreMessage = overallScore >= 80
    ? 'Excellent!'
    : overallScore >= 60
      ? 'Good, room for improvement'
      : 'Needs attention';

  return (
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
                {overallScore.toFixed(0)}
              </Typography>
              <Typography variant="h4">
                {getScoreGrade(overallScore)}
              </Typography>
              <Typography variant="body2" sx={{ mt: 2, opacity: 0.9 }}>
                {scoreMessage}
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
                  <RechartsTooltip />
                </RadarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Business Impact Metrics */}
      <Box display="flex" alignItems="center" sx={{ mt: 4, mb: 2 }}>
        <Assessment sx={{ mr: 1 }} />
        <Typography variant="h5">
          Business Impact
        </Typography>
      </Box>
      <Grid container spacing={3} sx={{ mb: 3 }}>
        {businessMetrics.map((metric, index) => (
          <Grid item xs={12} sm={6} md={3} key={index}>
            <ScoreCard {...metric} />
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
            <RechartsTooltip />
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
  );
}
