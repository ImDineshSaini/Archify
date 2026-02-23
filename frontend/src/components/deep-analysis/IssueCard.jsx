import React from 'react';
import {
  Box,
  Typography,
  Chip,
  Card,
  CardContent,
} from '@mui/material';
import {
  Info as InfoIcon,
  Build as BuildIcon,
  Rocket as RocketIcon,
  AccessTime as TimeIcon,
  LocalFireDepartment as FireIcon,
  Bolt as BoltIcon,
  Star as StarIcon,
  EmojiEvents as TrophyIcon,
  BusinessCenter as BusinessCenterIcon,
} from '@mui/icons-material';
import { getPriorityColor } from '../../utils/statusColors'; // available for consumers

/**
 * Returns the MUI icon for a given priority level.
 */
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

/**
 * Returns the gradient background for a priority chip.
 */
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

/**
 * Returns the left-border colour for a given priority level.
 */
const getBorderColor = (priority) => {
  switch (priority?.toLowerCase?.() || '') {
    case 'critical': return '#d32f2f';
    case 'high':     return '#f57c00';
    case 'medium':   return '#1976d2';
    default:         return '#388e3c';
  }
};

/**
 * IssueCard -- renders a single issue with priority badge, location,
 * evidence, fix, expected impact, effort and business impact.
 */
const IssueCard = ({ issue, index }) => (
  <Card
    key={index}
    sx={{
      mb: 2,
      borderLeft: `5px solid ${getBorderColor(issue.priority)}`,
      boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
      transition: 'transform 0.2s, box-shadow 0.2s',
      '&:hover': {
        transform: 'translateY(-2px)',
        boxShadow: '0 4px 16px rgba(0,0,0,0.15)',
      },
    }}
  >
    <CardContent>
      {/* Header row: icon + title + priority chip */}
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
            boxShadow: '0 2px 4px rgba(0,0,0,0.2)',
          }}
          size="small"
        />
      </Box>

      {/* Location */}
      {issue.location && (
        <Box sx={{ mb: 1, p: 1, bgcolor: '#f5f5f5', borderRadius: 1 }}>
          <Typography variant="body2" sx={{ fontFamily: 'monospace' }}>
            <strong>Location:</strong>{' '}
            <code style={{ color: '#d32f2f' }}>{issue.location}</code>
          </Typography>
        </Box>
      )}

      {/* Evidence */}
      {issue.evidence && (
        <Typography
          variant="body2"
          color="text.secondary"
          sx={{ mb: 1, pl: 2, borderLeft: '3px solid #e0e0e0' }}
        >
          <strong>Evidence:</strong> {issue.evidence}
        </Typography>
      )}

      {/* Fix / Refactoring */}
      {(issue.fix || issue.refactoring) && (
        <Box
          sx={{
            mt: 2,
            p: 2,
            borderRadius: 2,
            background: 'linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 100%)',
            border: '1px solid #a5d6a7',
          }}
        >
          <Typography variant="body2" sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <BuildIcon sx={{ color: '#2e7d32', fontSize: 20 }} />
            <strong>Fix:</strong>
          </Typography>
          <Typography variant="body2" sx={{ mt: 0.5, pl: 3 }}>
            {issue.fix || issue.refactoring}
          </Typography>
        </Box>
      )}

      {/* Expected Impact */}
      {issue.expected_improvement && (
        <Box sx={{ mt: 1, display: 'flex', alignItems: 'center', gap: 1, p: 1, bgcolor: '#e3f2fd', borderRadius: 1 }}>
          <RocketIcon sx={{ color: '#1976d2', fontSize: 20 }} />
          <Typography variant="body2" sx={{ fontWeight: 500 }}>
            <strong>Expected Impact:</strong> {issue.expected_improvement}
          </Typography>
        </Box>
      )}

      {/* Effort */}
      {issue.effort_hours && (
        <Box sx={{ mt: 1, display: 'flex', alignItems: 'center', gap: 1 }}>
          <TimeIcon fontSize="small" sx={{ color: '#757575' }} />
          <Typography variant="body2" color="text.secondary">
            <strong>Effort:</strong> {issue.effort_hours} hours
          </Typography>
        </Box>
      )}

      {/* Business Impact */}
      {issue.business_impact && (
        <Box sx={{ mt: 1, p: 1, bgcolor: '#ffebee', borderRadius: 1, borderLeft: '4px solid #d32f2f' }}>
          <Typography variant="body2" sx={{ color: '#c62828', fontWeight: 500, display: 'flex', alignItems: 'center', gap: 0.5 }}>
            <BusinessCenterIcon sx={{ fontSize: 18 }} />
            <strong>Business Impact:</strong> {issue.business_impact}
          </Typography>
        </Box>
      )}
    </CardContent>
  </Card>
);

export default IssueCard;
