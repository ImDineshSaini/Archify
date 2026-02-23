/**
 * Shared status/score color utilities used across Dashboard,
 * AnalysisDetailEnhanced, AnalysisHistory, and DeepAnalysisView.
 */

export const getStatusColor = (status) => {
  const colors = {
    completed: 'success',
    running: 'info',
    pending: 'warning',
    failed: 'error',
  };
  return colors[status] || 'default';
};

export const getScoreColor = (score) => {
  if (score >= 80) return '#4caf50';
  if (score >= 60) return '#ff9800';
  return '#f44336';
};

export const getScoreGrade = (score) => {
  if (score >= 95) return 'A+';
  if (score >= 90) return 'A';
  if (score >= 85) return 'A-';
  if (score >= 80) return 'B+';
  if (score >= 75) return 'B';
  if (score >= 70) return 'B-';
  if (score >= 65) return 'C+';
  if (score >= 60) return 'C';
  if (score >= 55) return 'C-';
  if (score >= 50) return 'D';
  return 'F';
};

export const getPriorityColor = (priority) => {
  switch ((priority || '').toLowerCase()) {
    case 'critical': return 'error';
    case 'high': return 'warning';
    case 'medium': return 'info';
    case 'low': return 'success';
    default: return 'default';
  }
};
