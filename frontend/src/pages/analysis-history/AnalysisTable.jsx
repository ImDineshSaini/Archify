import {
  Typography,
  Box,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TablePagination,
  Chip,
  IconButton,
  Tooltip,
  Menu,
  MenuItem,
  ListItemIcon,
  ListItemText,
} from '@mui/material';
import {
  Visibility,
  Delete,
  MoreVert,
  CheckCircle,
  Error,
  HourglassEmpty,
} from '@mui/icons-material';
import { getStatusColor, getScoreColor } from '../../utils/statusColors';

function getStatusIcon(status) {
  const icons = {
    completed: <CheckCircle />,
    running: <HourglassEmpty />,
    pending: <HourglassEmpty />,
    failed: <Error />,
  };
  return icons[status] || <HourglassEmpty />;
}

function AnalysisTable({
  loading,
  paginatedAnalyses,
  repositories,
  filteredCount,
  page,
  rowsPerPage,
  onPageChange,
  onRowsPerPageChange,
  onView,
  onDelete,
  anchorEl,
  selectedAnalysis,
  onMenuOpen,
  onMenuClose,
}) {
  return (
    <>
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>ID</TableCell>
              <TableCell>Repository</TableCell>
              <TableCell>Status</TableCell>
              <TableCell>Overall Score</TableCell>
              <TableCell>Duration</TableCell>
              <TableCell>Created At</TableCell>
              <TableCell align="right">Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {loading ? (
              <TableRow>
                <TableCell colSpan={7} align="center">
                  Loading...
                </TableCell>
              </TableRow>
            ) : paginatedAnalyses.length === 0 ? (
              <TableRow>
                <TableCell colSpan={7} align="center">
                  No analyses found
                </TableCell>
              </TableRow>
            ) : (
              paginatedAnalyses.map((analysis) => {
                const repo = repositories[analysis.repository_id];

                return (
                  <TableRow key={analysis.id} hover sx={{ cursor: 'pointer' }}>
                    <TableCell onClick={() => onView(analysis)}>#{analysis.id}</TableCell>
                    <TableCell onClick={() => onView(analysis)}>
                      <Box>
                        <Typography variant="body2" fontWeight="bold">
                          {repo?.name || 'Unknown'}
                        </Typography>
                        {repo?.language && (
                          <Chip label={repo.language} size="small" sx={{ mt: 0.5 }} />
                        )}
                      </Box>
                    </TableCell>
                    <TableCell onClick={() => onView(analysis)}>
                      <Chip
                        icon={getStatusIcon(analysis.status)}
                        label={analysis.status}
                        color={getStatusColor(analysis.status)}
                        size="small"
                      />
                    </TableCell>
                    <TableCell onClick={() => onView(analysis)}>
                      {analysis.overall_score != null ? (
                        <Chip
                          label={`${analysis.overall_score.toFixed(0)}/100`}
                          color={getScoreColor(analysis.overall_score)}
                          size="small"
                        />
                      ) : (
                        '-'
                      )}
                    </TableCell>
                    <TableCell onClick={() => onView(analysis)}>
                      {analysis.analysis_duration
                        ? `${analysis.analysis_duration.toFixed(1)}s`
                        : '-'}
                    </TableCell>
                    <TableCell onClick={() => onView(analysis)}>
                      {new Date(analysis.created_at).toLocaleString()}
                    </TableCell>
                    <TableCell align="right">
                      <Tooltip title="View Details">
                        <IconButton size="small" onClick={() => onView(analysis)}>
                          <Visibility />
                        </IconButton>
                      </Tooltip>
                      <Tooltip title="More Actions">
                        <IconButton
                          size="small"
                          onClick={(e) => onMenuOpen(e, analysis)}
                        >
                          <MoreVert />
                        </IconButton>
                      </Tooltip>
                    </TableCell>
                  </TableRow>
                );
              })
            )}
          </TableBody>
        </Table>

        <TablePagination
          rowsPerPageOptions={[5, 10, 25, 50, 100]}
          component="div"
          count={filteredCount}
          rowsPerPage={rowsPerPage}
          page={page}
          onPageChange={onPageChange}
          onRowsPerPageChange={onRowsPerPageChange}
        />
      </TableContainer>

      {/* Context Menu */}
      <Menu anchorEl={anchorEl} open={Boolean(anchorEl)} onClose={onMenuClose}>
        <MenuItem onClick={() => onView(selectedAnalysis)}>
          <ListItemIcon>
            <Visibility fontSize="small" />
          </ListItemIcon>
          <ListItemText>View Details</ListItemText>
        </MenuItem>
        <MenuItem onClick={() => onDelete(selectedAnalysis)}>
          <ListItemIcon>
            <Delete fontSize="small" color="error" />
          </ListItemIcon>
          <ListItemText>Delete</ListItemText>
        </MenuItem>
      </Menu>
    </>
  );
}

export default AnalysisTable;
