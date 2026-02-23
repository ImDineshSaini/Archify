import {
  Typography,
  Paper,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Grid,
} from '@mui/material';

function FiltersBar({
  searchQuery,
  onSearchChange,
  filterStatus,
  onFilterStatusChange,
  filterRepo,
  onFilterRepoChange,
  repositories,
  resultCount,
}) {
  return (
    <Paper sx={{ p: 2, mb: 3 }}>
      <Grid container spacing={2} alignItems="center">
        <Grid item xs={12} md={4}>
          <TextField
            fullWidth
            label="Search by repository"
            variant="outlined"
            value={searchQuery}
            onChange={(e) => onSearchChange(e.target.value)}
            size="small"
          />
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <FormControl fullWidth size="small">
            <InputLabel>Status</InputLabel>
            <Select
              value={filterStatus}
              label="Status"
              onChange={(e) => onFilterStatusChange(e.target.value)}
            >
              <MenuItem value="all">All Statuses</MenuItem>
              <MenuItem value="completed">Completed</MenuItem>
              <MenuItem value="running">Running</MenuItem>
              <MenuItem value="pending">Pending</MenuItem>
              <MenuItem value="failed">Failed</MenuItem>
            </Select>
          </FormControl>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <FormControl fullWidth size="small">
            <InputLabel>Repository</InputLabel>
            <Select
              value={filterRepo}
              label="Repository"
              onChange={(e) => onFilterRepoChange(e.target.value)}
            >
              <MenuItem value="all">All Repositories</MenuItem>
              {Object.values(repositories).map((repo) => (
                <MenuItem key={repo.id} value={repo.id}>
                  {repo.name}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
        </Grid>

        <Grid item xs={12} md={2}>
          <Typography variant="body2" color="text.secondary">
            {resultCount} results
          </Typography>
        </Grid>
      </Grid>
    </Paper>
  );
}

export default FiltersBar;
