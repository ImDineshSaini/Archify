import {
  Typography,
  Box,
  Paper,
  Grid,
  Card,
  CardContent,
  Divider,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
} from '@mui/material';
import {
  TrendingUp,
  CheckCircle,
  Warning,
  Error as ErrorIcon,
  InsertDriveFile,
  Code,
  Comment,
  Folder,
  FlashOn,
  AccountTree,
  Sync,
  Assessment,
  BugReport,
} from '@mui/icons-material';

/**
 * Map a metric label to its corresponding MUI icon element.
 */
const metricIconMap = {
  'Total Lines': <InsertDriveFile />,
  'Code Lines': <Code />,
  'Comment Lines': <Comment />,
  'Files Analyzed': <Folder />,
  'Functions': <FlashOn />,
  'Classes': <AccountTree />,
  'Avg Complexity': <Sync />,
  'Comment Ratio': <Assessment />,
};

/**
 * Build code metrics array from the analysis data, using MUI icons
 * instead of emoji characters.
 */
function buildCodeMetrics(codeMetrics) {
  return [
    { label: 'Total Lines', value: codeMetrics.total_lines?.toLocaleString() },
    { label: 'Code Lines', value: codeMetrics.code_lines?.toLocaleString() },
    { label: 'Comment Lines', value: codeMetrics.comment_lines?.toLocaleString() },
    { label: 'Files Analyzed', value: codeMetrics.files_analyzed },
    { label: 'Functions', value: codeMetrics.functions || 'N/A' },
    { label: 'Classes', value: codeMetrics.classes || 'N/A' },
    { label: 'Avg Complexity', value: codeMetrics.avg_complexity?.toFixed(1) || 'N/A' },
    {
      label: 'Comment Ratio',
      value: `${((codeMetrics.comment_lines / codeMetrics.total_lines) * 100).toFixed(1)}%`,
    },
  ];
}

/**
 * Code Quality tab (tab 5) – code metrics grid and issues list.
 */
export default function CodeQualityTab({ analysis }) {
  return (
    <>
      <Box display="flex" alignItems="center" sx={{ mb: 3 }}>
        <TrendingUp sx={{ mr: 1 }} />
        <Typography variant="h5">
          Code Quality Metrics
        </Typography>
      </Box>

      {/* Code Metrics Grid */}
      {analysis.code_metrics && (
        <Grid container spacing={3} sx={{ mb: 3 }}>
          {buildCodeMetrics(analysis.code_metrics).map((metric, index) => (
            <Grid item xs={6} md={3} key={index}>
              <Card>
                <CardContent>
                  <Box sx={{ mb: 1, color: 'primary.main' }}>
                    {metricIconMap[metric.label]}
                  </Box>
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
          <Box display="flex" alignItems="center" sx={{ mb: 1 }}>
            <BugReport sx={{ mr: 1 }} />
            <Typography variant="h6">
              Issues Found ({analysis.issues.length})
            </Typography>
          </Box>
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
                      {' \u2022 '}
                      <Typography component="span" variant="body2" color="text.primary">
                        Severity: {issue.severity}
                      </Typography>
                      {issue.file && (
                        <>
                          {' \u2022 '}
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
  );
}
