import {
  Typography,
  Box,
  Paper,
  Grid,
  Card,
  CardContent,
  Chip,
  Divider,
  Alert,
} from '@mui/material';
import {
  Lightbulb,
  Description,
} from '@mui/icons-material';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';
import { getPriorityColor } from '../../utils/statusColors';

// Markdown rendering components for code highlighting
const markdownComponents = {
  code({ node, inline, className, children, ...props }) {
    const match = /language-(\w+)/.exec(className || '');
    return !inline && match ? (
      <SyntaxHighlighter
        style={vscDarkPlus}
        language={match[1]}
        PreTag="div"
        {...props}
      >
        {String(children).replace(/\n$/, '')}
      </SyntaxHighlighter>
    ) : (
      <code className={className} {...props}>
        {children}
      </code>
    );
  },
};

// Static AI suggestion stubs
const aiSuggestions = [
  {
    priority: 'HIGH',
    category: 'Security',
    title: 'Fix Critical Security Vulnerabilities',
    description: 'Found 3 critical security issues that could lead to data breaches',
    impact: 'High business risk, potential data loss',
    effort: '2-3 days',
    roi: 'High',
  },
  {
    priority: 'MEDIUM',
    category: 'Maintainability',
    title: 'Refactor Complex Functions',
    description: '15 functions exceed complexity threshold (cyclomatic > 10)',
    impact: 'Slower development, more bugs',
    effort: '5-7 days',
    roi: 'Medium',
  },
  {
    priority: 'LOW',
    category: 'Performance',
    title: 'Optimize Database Queries',
    description: 'Identify N+1 queries and missing indexes',
    impact: 'Better user experience',
    effort: '1-2 days',
    roi: 'Medium',
  },
];

/**
 * AI Insights tab (tab 4) – prioritised AI-powered recommendations
 * and the full markdown AI analysis report.
 */
export default function AIInsightsTab({ analysis }) {
  return (
    <>
      <Box display="flex" alignItems="center" sx={{ mb: 3 }}>
        <Lightbulb sx={{ mr: 1 }} />
        <Typography variant="h5">
          AI-Powered Recommendations
        </Typography>
      </Box>

      <Alert severity="info" sx={{ mb: 3 }}>
        <Typography variant="body1">
          <strong>Our AI analyzed {analysis.code_metrics?.files_analyzed || 0} files</strong> and found actionable improvements ranked by business impact.
        </Typography>
      </Alert>

      {aiSuggestions.map((suggestion, index) => (
        <Card key={index} sx={{ mb: 3 }}>
          <CardContent>
            <Box display="flex" alignItems="center" mb={2}>
              <Chip
                label={suggestion.priority}
                color={getPriorityColor(suggestion.priority)}
                size="small"
                sx={{ mr: 2, fontWeight: 'bold' }}
              />
              <Chip label={suggestion.category} variant="outlined" size="small" sx={{ mr: 2 }} />
              <Typography variant="h6" sx={{ flexGrow: 1 }}>
                {suggestion.title}
              </Typography>
            </Box>

            <Typography variant="body1" paragraph>
              {suggestion.description}
            </Typography>

            <Grid container spacing={2} sx={{ mt: 2 }}>
              <Grid item xs={12} sm={4}>
                <Box>
                  <Typography variant="caption" color="text.secondary">
                    Business Impact
                  </Typography>
                  <Typography variant="body2" fontWeight="bold">
                    {suggestion.impact}
                  </Typography>
                </Box>
              </Grid>
              <Grid item xs={12} sm={4}>
                <Box>
                  <Typography variant="caption" color="text.secondary">
                    Effort Required
                  </Typography>
                  <Typography variant="body2" fontWeight="bold">
                    {suggestion.effort}
                  </Typography>
                </Box>
              </Grid>
              <Grid item xs={12} sm={4}>
                <Box>
                  <Typography variant="caption" color="text.secondary">
                    ROI
                  </Typography>
                  <Chip
                    label={suggestion.roi}
                    color={suggestion.roi === 'High' ? 'success' : 'warning'}
                    size="small"
                  />
                </Box>
              </Grid>
            </Grid>
          </CardContent>
        </Card>
      ))}

      {/* Full AI Report with Markdown */}
      {analysis.suggestions && (
        <Paper sx={{ p: 3, mt: 3 }}>
          <Box display="flex" alignItems="center" sx={{ mb: 1 }}>
            <Description sx={{ mr: 1 }} />
            <Typography variant="h6">
              Detailed AI Analysis Report
            </Typography>
          </Box>
          <Divider sx={{ mb: 2 }} />
          <ReactMarkdown
            remarkPlugins={[remarkGfm]}
            components={markdownComponents}
          >
            {analysis.suggestions}
          </ReactMarkdown>
        </Paper>
      )}
    </>
  );
}
