import React from 'react';
import {
  Box,
  Typography,
  Alert,
  Paper,
} from '@mui/material';
import {
  Info as InfoIcon,
} from '@mui/icons-material';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import IssueCard from './IssueCard';
import RecommendationList from './RecommendationList';

/**
 * Human-readable heading for a layer.
 */
const getLayerHeading = (layerName) => {
  switch (layerName) {
    case 'security':     return 'Security Issues';
    case 'performance':  return 'Performance Bottlenecks';
    case 'testing':      return 'Test Coverage Gaps';
    case 'devops':       return 'DevOps Gaps';
    case 'code_quality': return 'Code Quality Issues';
    default:             return 'Issues';
  }
};

/** Markdown styling applied to raw-analysis fallback blocks. */
const markdownSx = {
  '& h1, & h2, & h3': { mt: 2, mb: 1 },
  '& ul, & ol': { pl: 3 },
  '& li': { mb: 0.5 },
  '& p': { mb: 1 },
  '& code': {
    bgcolor: '#e0e0e0',
    px: 0.5,
    py: 0.25,
    borderRadius: 1,
    fontSize: '0.9em',
  },
  '& pre': {
    bgcolor: '#263238',
    color: '#fff',
    p: 2,
    borderRadius: 1,
    overflow: 'auto',
  },
};

/**
 * Try to extract structured issue/recommendation data from a raw_analysis
 * string that may be JSON or contain a JSON code-block.
 */
const tryParseRaw = (rawAnalysis) => {
  const rawContent =
    typeof rawAnalysis === 'string'
      ? rawAnalysis
      : JSON.stringify(rawAnalysis, null, 2);

  let parsedData = null;
  try {
    parsedData = JSON.parse(rawContent);
  } catch {
    const jsonMatch = rawContent.match(/```(?:json)?\s*\n?([\s\S]*?)\n?```/);
    if (jsonMatch) {
      try {
        parsedData = JSON.parse(jsonMatch[1]);
      } catch (e) {
        // intentionally ignored -- fall through to markdown
      }
    }
  }

  return { parsedData, rawContent };
};

/**
 * Picks the first non-empty issue array from a data object.
 */
const pickIssues = (data) =>
  data.critical_issues ||
  data.bottlenecks ||
  data.coverage_gaps ||
  data.missing_devops ||
  data.quality_issues ||
  [];

/**
 * LayerAnalysisTab -- renders the analysis for a single architecture layer
 * (security, performance, testing, devops, code_quality).
 */
const LayerAnalysisTab = ({ layerName, layerData }) => {
  if (!layerData || layerData.error) {
    return (
      <Alert severity="warning">
        <Typography>
          {layerName} analysis failed: {layerData?.error || 'Unknown error'}
        </Typography>
      </Alert>
    );
  }

  const issues = pickIssues(layerData);
  const recommendations = layerData.recommendations || [];

  return (
    <Box>
      {/* Structured issues */}
      {issues.length > 0 ? (
        <Box sx={{ mb: 3 }}>
          <Typography variant="h6" sx={{ mb: 2 }}>
            {issues.length} {getLayerHeading(layerName)}
          </Typography>
          {issues.map((issue, index) => (
            <IssueCard key={index} issue={issue} index={index} />
          ))}
        </Box>
      ) : (
        <Alert severity="success" sx={{ mb: 3 }}>
          <Typography>No critical issues found in {layerName} analysis!</Typography>
        </Alert>
      )}

      {/* Recommendations */}
      <RecommendationList recommendations={recommendations} />

      {/* Raw analysis fallback */}
      {layerData.raw_analysis && issues.length === 0 && (() => {
        const { parsedData, rawContent } = tryParseRaw(layerData.raw_analysis);

        if (
          parsedData &&
          (parsedData.critical_issues ||
            parsedData.bottlenecks ||
            parsedData.coverage_gaps ||
            parsedData.missing_devops ||
            parsedData.quality_issues ||
            parsedData.recommendations)
        ) {
          const parsedIssues = pickIssues(parsedData);
          const parsedRecommendations = parsedData.recommendations || [];

          return (
            <Box>
              {parsedIssues.length > 0 && (
                <Box sx={{ mb: 3 }}>
                  <Typography variant="h6" sx={{ mb: 2 }}>
                    {parsedIssues.length} {getLayerHeading(layerName)}
                  </Typography>
                  {parsedIssues.map((issue, index) => (
                    <IssueCard key={index} issue={issue} index={index} />
                  ))}
                </Box>
              )}
              <RecommendationList recommendations={parsedRecommendations} />
            </Box>
          );
        }

        // Markdown fallback
        return (
          <Paper sx={{ p: 3, bgcolor: '#f5f5f5' }}>
            <Alert severity="warning" sx={{ mb: 2 }}>
              <Typography variant="body2">
                <InfoIcon fontSize="small" sx={{ verticalAlign: 'middle', mr: 1 }} />
                Unable to parse structured analysis. Showing raw AI response:
              </Typography>
            </Alert>
            <Box sx={markdownSx}>
              <ReactMarkdown remarkPlugins={[remarkGfm]}>
                {rawContent}
              </ReactMarkdown>
            </Box>
          </Paper>
        );
      })()}
    </Box>
  );
};

export default LayerAnalysisTab;
