import React from 'react';
import {
  Box,
  Typography,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
} from '@mui/material';
import {
  FlashOn as FlashOnIcon,
  Diamond as DiamondIcon,
} from '@mui/icons-material';

/**
 * RecommendationList -- renders a styled list of improvement recommendations.
 */
const RecommendationList = ({ recommendations }) => {
  if (!recommendations || recommendations.length === 0) return null;

  return (
    <Box
      sx={{
        mt: 3,
        p: 3,
        borderRadius: 2,
        background: 'linear-gradient(135deg, #f3e5f5 0%, #e1bee7 100%)',
        border: '1px solid #ce93d8',
      }}
    >
      <Typography
        variant="h6"
        sx={{ mb: 2, display: 'flex', alignItems: 'center', gap: 1 }}
      >
        <DiamondIcon sx={{ color: '#7b1fa2' }} />
        Recommended Improvements
      </Typography>
      <List sx={{ bgcolor: 'rgba(255,255,255,0.6)', borderRadius: 1 }}>
        {recommendations.map((rec, index) => (
          <ListItem
            key={index}
            sx={{
              borderBottom:
                index < recommendations.length - 1
                  ? '1px solid #e0e0e0'
                  : 'none',
              '&:hover': { bgcolor: 'rgba(123, 31, 162, 0.05)' },
            }}
          >
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
  );
};

export default RecommendationList;
