import {
  Typography,
  Box,
  Grid,
  Card,
  CardContent,
} from '@mui/material';
import {
  TrendingUp,
  CheckCircle,
  Error,
  HourglassEmpty,
  Assessment,
} from '@mui/icons-material';

function StatsCards({ stats }) {
  const cards = [
    {
      icon: <Assessment sx={{ mr: 1, color: '#2196f3' }} />,
      label: 'Total Analyses',
      value: stats.total,
      color: 'primary',
    },
    {
      icon: <CheckCircle sx={{ mr: 1, color: '#4caf50' }} />,
      label: 'Completed',
      value: stats.completed,
      color: 'success.main',
    },
    {
      icon: <HourglassEmpty sx={{ mr: 1, color: '#ff9800' }} />,
      label: 'Running',
      value: stats.running,
      color: 'warning.main',
    },
    {
      icon: <Error sx={{ mr: 1, color: '#f44336' }} />,
      label: 'Failed',
      value: stats.failed,
      color: 'error.main',
    },
    {
      icon: <TrendingUp sx={{ mr: 1, color: '#9c27b0' }} />,
      label: 'Avg Score',
      value: stats.avgScore,
      color: 'secondary.main',
    },
  ];

  return (
    <Grid container spacing={3} sx={{ mb: 4 }}>
      {cards.map((card) => (
        <Grid item xs={12} sm={6} md={2.4} key={card.label}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" mb={1}>
                {card.icon}
                <Typography variant="h6" fontSize="0.9rem">
                  {card.label}
                </Typography>
              </Box>
              <Typography variant="h3" color={card.color}>
                {card.value}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      ))}
    </Grid>
  );
}

export default StatsCards;
