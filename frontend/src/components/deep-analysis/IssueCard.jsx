import { useState } from 'react';
import {
  Box,
  Typography,
  Chip,
  Card,
  CardContent,
  Collapse,
  IconButton,
  Menu,
  MenuItem,
  ListItemIcon,
  ListItemText,
  Tooltip,
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
  ExpandMore as ExpandMoreIcon,
  Flag as FlagIcon,
  CheckCircle as CheckCircleIcon,
  Cancel as CancelIcon,
  RadioButtonUnchecked as OpenIcon,
} from '@mui/icons-material';

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

const STATUS_CONFIG = {
  open: { label: 'Open', color: '#757575', icon: <OpenIcon sx={{ fontSize: 16 }} /> },
  false_positive: { label: 'False Positive', color: '#9e9e9e', icon: <CancelIcon sx={{ fontSize: 16 }} /> },
  accepted: { label: 'Accepted', color: '#f57c00', icon: <FlagIcon sx={{ fontSize: 16 }} /> },
  resolved: { label: 'Resolved', color: '#388e3c', icon: <CheckCircleIcon sx={{ fontSize: 16 }} /> },
};

/**
 * IssueCard -- renders a single issue as a compact, expandable card.
 * Collapsed: shows #number + issue title + category + priority chip + status chip.
 * Expanded: reveals location, evidence, fix, effort, business impact, and status controls.
 */
/**
 * Strips local temp directory prefix from a path and builds a URL to the file
 * in the original repo (GitHub/GitLab).
 */
const buildFileUrl = (location, repoUrl) => {
  if (!location || !repoUrl) return null;
  // Strip temp clone dir: "archify_repo_xxxx/" or "/tmp/..."
  let cleanPath = location.replace(/^\/?(archify_repo_\w+|\/tmp\/[^/]+)\/?/, '');
  cleanPath = cleanPath.replace(/^\//, '');
  if (!cleanPath) return repoUrl;
  // Normalize repo URL
  let base = repoUrl.replace(/\/$/, '').replace(/\.git$/, '');
  if (base.toLowerCase().includes('gitlab')) {
    return `${base}/-/blob/main/${cleanPath}`;
  }
  return `${base}/blob/main/${cleanPath}`;
};

/**
 * Returns the clean display path (without temp dir prefix).
 */
const cleanLocationPath = (location) => {
  if (!location) return '';
  return location.replace(/^\/?(archify_repo_\w+|\/tmp\/[^/]+)\/?/, '').replace(/^\//, '') || location;
};

const IssueCard = ({ issue, index, repoUrl, issueStatus, onStatusChange }) => {
  const [expanded, setExpanded] = useState(false);
  const [statusMenuAnchor, setStatusMenuAnchor] = useState(null);

  const currentStatus = issueStatus || 'open';
  const statusConfig = STATUS_CONFIG[currentStatus] || STATUS_CONFIG.open;
  const isMuted = currentStatus === 'false_positive' || currentStatus === 'resolved';

  const handleStatusClick = (e) => {
    e.stopPropagation();
    setStatusMenuAnchor(e.currentTarget);
  };

  const handleStatusSelect = (newStatus) => {
    setStatusMenuAnchor(null);
    if (onStatusChange) {
      onStatusChange(newStatus);
    }
  };

  return (
    <Card
      sx={{
        mb: 1.5,
        borderLeft: `5px solid ${getBorderColor(issue.priority)}`,
        boxShadow: expanded
          ? '0 4px 16px rgba(0,0,0,0.15)'
          : '0 1px 4px rgba(0,0,0,0.08)',
        cursor: 'pointer',
        transition: 'box-shadow 0.2s, opacity 0.2s',
        opacity: isMuted ? 0.6 : 1,
        '&:hover': {
          boxShadow: '0 2px 10px rgba(0,0,0,0.12)',
          opacity: 1,
        },
      }}
      onClick={() => setExpanded(!expanded)}
    >
      <CardContent sx={{ py: 1.5, '&:last-child': { pb: 1.5 } }}>
        {/* Header row: always visible */}
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <Typography
            variant="body2"
            sx={{
              fontWeight: 700,
              color: getBorderColor(issue.priority),
              minWidth: 28,
            }}
          >
            #{index + 1}
          </Typography>
          {getPriorityIcon(issue.priority)}
          <Typography
            variant="subtitle2"
            sx={{
              flex: 1,
              fontWeight: 600,
              textDecoration: currentStatus === 'resolved' ? 'line-through' : 'none',
            }}
            noWrap={!expanded}
          >
            {issue.issue || issue.message || issue.gap || issue.missing_tests_for || 'Issue'}
          </Typography>
          {issue.category && (
            <Chip
              label={issue.category}
              size="small"
              variant="outlined"
              sx={{ fontSize: '0.7rem', height: 22, display: { xs: 'none', sm: 'flex' } }}
            />
          )}
          {/* Status chip */}
          {onStatusChange && (
            <Tooltip title="Click to change status">
              <Chip
                icon={statusConfig.icon}
                label={statusConfig.label}
                size="small"
                variant={currentStatus === 'open' ? 'outlined' : 'filled'}
                onClick={handleStatusClick}
                sx={{
                  fontSize: '0.65rem',
                  height: 22,
                  ...(currentStatus !== 'open' && {
                    bgcolor: statusConfig.color,
                    color: 'white',
                    '& .MuiChip-icon': { color: 'white' },
                  }),
                }}
              />
            </Tooltip>
          )}
          <Chip
            label={issue.priority || 'Medium'}
            sx={{
              background: getPriorityGradient(issue.priority),
              color: 'white',
              fontWeight: 600,
              fontSize: '0.7rem',
              height: 24,
            }}
            size="small"
          />
          {issue.effort_hours && (
            <Chip
              icon={<TimeIcon sx={{ fontSize: '14px !important' }} />}
              label={`${issue.effort_hours}h`}
              size="small"
              variant="outlined"
              sx={{ fontSize: '0.7rem', height: 22, display: { xs: 'none', md: 'flex' } }}
            />
          )}
          <IconButton
            size="small"
            sx={{
              transform: expanded ? 'rotate(180deg)' : 'rotate(0deg)',
              transition: 'transform 0.2s',
              ml: 0.5,
            }}
            onClick={(e) => { e.stopPropagation(); setExpanded(!expanded); }}
          >
            <ExpandMoreIcon fontSize="small" />
          </IconButton>
        </Box>

        {/* Status change menu */}
        <Menu
          anchorEl={statusMenuAnchor}
          open={Boolean(statusMenuAnchor)}
          onClose={(e) => { e.stopPropagation?.(); setStatusMenuAnchor(null); }}
          onClick={(e) => e.stopPropagation()}
        >
          {Object.entries(STATUS_CONFIG).map(([key, config]) => (
            <MenuItem
              key={key}
              selected={key === currentStatus}
              onClick={() => handleStatusSelect(key)}
            >
              <ListItemIcon>{config.icon}</ListItemIcon>
              <ListItemText>{config.label}</ListItemText>
            </MenuItem>
          ))}
        </Menu>

        {/* Expandable details */}
        <Collapse in={expanded}>
          <Box sx={{ mt: 2, pl: 4.5 }}>
            {/* Location */}
            {issue.location && (
              <Box sx={{ mb: 1, p: 1, bgcolor: '#f5f5f5', borderRadius: 1 }}>
                <Typography variant="body2" sx={{ fontFamily: 'monospace' }}>
                  <strong>Location:</strong>{' '}
                  {(() => {
                    const fileUrl = buildFileUrl(issue.location, repoUrl);
                    const displayPath = cleanLocationPath(issue.location);
                    if (fileUrl) {
                      return (
                        <a
                          href={fileUrl}
                          target="_blank"
                          rel="noopener noreferrer"
                          style={{ color: '#1565c0', textDecoration: 'underline' }}
                          onClick={(e) => e.stopPropagation()}
                        >
                          {displayPath}
                        </a>
                      );
                    }
                    return <code style={{ color: '#d32f2f' }}>{displayPath}</code>;
                  })()}
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
                  mt: 1.5,
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

            {/* Dependencies */}
            {issue.dependencies && issue.dependencies.length > 0 && (
              <Box sx={{ mt: 1, display: 'flex', alignItems: 'center', gap: 1, flexWrap: 'wrap' }}>
                <Typography variant="body2" color="text.secondary">
                  <strong>Dependencies:</strong>
                </Typography>
                {issue.dependencies.map((dep, i) => (
                  <Chip key={i} label={dep} size="small" variant="outlined" sx={{ fontSize: '0.7rem' }} />
                ))}
              </Box>
            )}
          </Box>
        </Collapse>
      </CardContent>
    </Card>
  );
};

export default IssueCard;
