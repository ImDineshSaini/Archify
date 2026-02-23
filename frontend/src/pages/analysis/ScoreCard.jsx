import { Box, Card, CardContent, Typography } from '@mui/material';

/**
 * Reusable score card component that displays a business metric
 * with an icon, value, unit, and description.
 */
export default function ScoreCard({ name, value, unit, icon, color, description }) {
  return (
    <Card>
      <CardContent>
        <Box display="flex" alignItems="center" mb={2}>
          <Box sx={{ color, mr: 1 }}>
            {icon}
          </Box>
          <Typography variant="h6">{name}</Typography>
        </Box>
        <Typography variant="h3" color={color}>
          {value.toFixed(0)}
          <Typography component="span" variant="h6" color="text.secondary">
            {unit}
          </Typography>
        </Typography>
        <Typography variant="caption" color="text.secondary">
          {description}
        </Typography>
      </CardContent>
    </Card>
  );
}
