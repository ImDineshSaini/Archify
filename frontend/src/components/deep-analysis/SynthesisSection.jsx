import React, { useState } from 'react';
import {
  Box,
  Typography,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Chip,
  Alert,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Paper,
} from '@mui/material';
import {
  ExpandMore as ExpandMoreIcon,
  Info as InfoIcon,
  FlashOn as FlashOnIcon,
  Bolt as BoltIcon,
  Star as StarIcon,
  LocalFireDepartment as FireIcon,
  EmojiEvents as TrophyIcon,
} from '@mui/icons-material';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import IssueCard from './IssueCard';

/** Markdown styling for the raw-analysis fallback block. */
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
 * Renders the structured (parsed) synthesis data: executive summary,
 * quick wins, and prioritised issue accordions.
 */
const ParsedSynthesis = ({ data, issueStatuses, repoUrl, onIssueStatusChange }) => {
  const [expandedPanel, setExpandedPanel] = useState(false);

  const toggle = (panel) =>
    setExpandedPanel(expandedPanel === panel ? false : panel);

  return (
    <Box>
      {/* Executive Summary */}
      {data.executive_summary && (
        <Alert severity="info" sx={{ mb: 3 }}>
          <Typography variant="h6" sx={{ mb: 1 }}>Executive Summary</Typography>
          <Typography variant="body1">{data.executive_summary}</Typography>
        </Alert>
      )}

      {/* Quick Wins */}
      {data.quick_wins && data.quick_wins.length > 0 && (
        <Box
          sx={{
            p: 3,
            mb: 3,
            borderRadius: 2,
            background: 'linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 100%)',
            border: '2px solid #66bb6a',
            boxShadow: '0 4px 12px rgba(76, 175, 80, 0.2)',
          }}
        >
          <Typography
            variant="h6"
            sx={{ mb: 2, display: 'flex', alignItems: 'center', gap: 1 }}
          >
            <FlashOnIcon sx={{ color: '#2e7d32', fontSize: 28 }} />
            <strong>Quick Wins</strong>
            <Chip
              label="< 4 hours each"
              sx={{
                ml: 1,
                background: 'linear-gradient(135deg, #4caf50 0%, #388e3c 100%)',
                color: 'white',
                fontWeight: 600,
              }}
              size="small"
            />
          </Typography>
          <List sx={{ bgcolor: 'rgba(255,255,255,0.7)', borderRadius: 1 }}>
            {data.quick_wins.map((win, index) => (
              <ListItem
                key={index}
                sx={{
                  borderBottom:
                    index < data.quick_wins.length - 1
                      ? '1px solid #e0e0e0'
                      : 'none',
                  '&:hover': { bgcolor: 'rgba(46, 125, 50, 0.05)' },
                }}
              >
                <ListItemIcon>
                  <StarIcon sx={{ color: '#ffc107' }} />
                </ListItemIcon>
                <ListItemText
                  primary={win}
                  sx={{ '& .MuiListItemText-primary': { fontWeight: 500 } }}
                />
              </ListItem>
            ))}
          </List>
        </Box>
      )}

      {/* Critical Issues */}
      {data.critical_issues && data.critical_issues.length > 0 && (
        <Accordion
          expanded={expandedPanel === 'critical'}
          onChange={() => toggle('critical')}
          sx={{
            mb: 2,
            borderRadius: '8px !important',
            boxShadow: '0 2px 8px rgba(211, 47, 47, 0.2)',
            '&:before': { display: 'none' },
          }}
        >
          <AccordionSummary
            expandIcon={<ExpandMoreIcon />}
            sx={{
              background: 'linear-gradient(135deg, #ffebee 0%, #ffcdd2 100%)',
              borderRadius: 1,
              '&:hover': { background: 'linear-gradient(135deg, #ffcdd2 0%, #ef9a9a 100%)' },
            }}
          >
            <Box sx={{ display: 'flex', alignItems: 'center', width: '100%', gap: 1 }}>
              <FireIcon sx={{ color: '#d32f2f', fontSize: 28 }} />
              <Typography variant="h6" sx={{ fontWeight: 700 }}>
                Critical Issues ({data.critical_issues.length})
              </Typography>
              <Chip
                label="Fix Immediately"
                sx={{
                  ml: 'auto',
                  background: 'linear-gradient(135deg, #d32f2f 0%, #c62828 100%)',
                  color: 'white',
                  fontWeight: 600,
                }}
                size="small"
              />
            </Box>
          </AccordionSummary>
          <AccordionDetails sx={{ bgcolor: '#fafafa', p: 3 }}>
            {data.critical_issues.map((issue, index) => (
              <IssueCard
                key={index}
                issue={issue}
                index={index}
                repoUrl={repoUrl}
                issueStatus={issueStatuses?.[`synthesis_critical:${index}`]}
                onStatusChange={onIssueStatusChange
                  ? (status) => onIssueStatusChange('synthesis_critical', index, status)
                  : undefined
                }
              />
            ))}
          </AccordionDetails>
        </Accordion>
      )}

      {/* High Priority */}
      {data.high_priority && data.high_priority.length > 0 && (
        <Accordion
          expanded={expandedPanel === 'high'}
          onChange={() => toggle('high')}
          sx={{
            mb: 2,
            borderRadius: '8px !important',
            boxShadow: '0 2px 8px rgba(245, 124, 0, 0.2)',
            '&:before': { display: 'none' },
          }}
        >
          <AccordionSummary
            expandIcon={<ExpandMoreIcon />}
            sx={{
              background: 'linear-gradient(135deg, #fff3e0 0%, #ffe0b2 100%)',
              borderRadius: 1,
              '&:hover': { background: 'linear-gradient(135deg, #ffe0b2 0%, #ffcc80 100%)' },
            }}
          >
            <Box sx={{ display: 'flex', alignItems: 'center', width: '100%', gap: 1 }}>
              <BoltIcon sx={{ color: '#f57c00', fontSize: 28 }} />
              <Typography variant="h6" sx={{ fontWeight: 700 }}>
                High Priority ({data.high_priority.length})
              </Typography>
              <Chip
                label="1-2 Sprints"
                sx={{
                  ml: 'auto',
                  background: 'linear-gradient(135deg, #f57c00 0%, #e65100 100%)',
                  color: 'white',
                  fontWeight: 600,
                }}
                size="small"
              />
            </Box>
          </AccordionSummary>
          <AccordionDetails sx={{ bgcolor: '#fafafa', p: 3 }}>
            {data.high_priority.map((issue, index) => (
              <IssueCard
                key={index}
                issue={issue}
                index={index}
                repoUrl={repoUrl}
                issueStatus={issueStatuses?.[`synthesis_high:${index}`]}
                onStatusChange={onIssueStatusChange
                  ? (status) => onIssueStatusChange('synthesis_high', index, status)
                  : undefined
                }
              />
            ))}
          </AccordionDetails>
        </Accordion>
      )}

      {/* Medium Priority */}
      {data.medium_priority && data.medium_priority.length > 0 && (
        <Accordion
          expanded={expandedPanel === 'medium'}
          onChange={() => toggle('medium')}
          sx={{
            mb: 2,
            borderRadius: '8px !important',
            boxShadow: '0 2px 8px rgba(25, 118, 210, 0.2)',
            '&:before': { display: 'none' },
          }}
        >
          <AccordionSummary
            expandIcon={<ExpandMoreIcon />}
            sx={{
              background: 'linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%)',
              borderRadius: 1,
              '&:hover': { background: 'linear-gradient(135deg, #bbdefb 0%, #90caf9 100%)' },
            }}
          >
            <Box sx={{ display: 'flex', alignItems: 'center', width: '100%', gap: 1 }}>
              <StarIcon sx={{ color: '#1976d2', fontSize: 28 }} />
              <Typography variant="h6" sx={{ fontWeight: 700 }}>
                Medium Priority ({data.medium_priority.length})
              </Typography>
              <Chip
                label="1-2 Months"
                sx={{
                  ml: 'auto',
                  background: 'linear-gradient(135deg, #1976d2 0%, #0d47a1 100%)',
                  color: 'white',
                  fontWeight: 600,
                }}
                size="small"
              />
            </Box>
          </AccordionSummary>
          <AccordionDetails sx={{ bgcolor: '#fafafa', p: 3 }}>
            {data.medium_priority.map((issue, index) => (
              <IssueCard
                key={index}
                issue={issue}
                index={index}
                repoUrl={repoUrl}
                issueStatus={issueStatuses?.[`synthesis_medium:${index}`]}
                onStatusChange={onIssueStatusChange
                  ? (status) => onIssueStatusChange('synthesis_medium', index, status)
                  : undefined
                }
              />
            ))}
          </AccordionDetails>
        </Accordion>
      )}

      {/* Low Priority */}
      {data.low_priority && data.low_priority.length > 0 && (
        <Accordion
          expanded={expandedPanel === 'low'}
          onChange={() => toggle('low')}
          sx={{
            mb: 2,
            borderRadius: '8px !important',
            boxShadow: '0 2px 8px rgba(56, 142, 60, 0.2)',
            '&:before': { display: 'none' },
          }}
        >
          <AccordionSummary
            expandIcon={<ExpandMoreIcon />}
            sx={{
              background: 'linear-gradient(135deg, #f1f8e9 0%, #dcedc8 100%)',
              borderRadius: 1,
              '&:hover': { background: 'linear-gradient(135deg, #dcedc8 0%, #c5e1a5 100%)' },
            }}
          >
            <Box sx={{ display: 'flex', alignItems: 'center', width: '100%', gap: 1 }}>
              <TrophyIcon sx={{ color: '#388e3c', fontSize: 28 }} />
              <Typography variant="h6" sx={{ fontWeight: 700 }}>
                Low Priority ({data.low_priority.length})
              </Typography>
              <Chip
                label="Nice to Have"
                sx={{
                  ml: 'auto',
                  background: 'linear-gradient(135deg, #388e3c 0%, #2e7d32 100%)',
                  color: 'white',
                  fontWeight: 600,
                }}
                size="small"
              />
            </Box>
          </AccordionSummary>
          <AccordionDetails sx={{ bgcolor: '#fafafa', p: 3 }}>
            {data.low_priority.map((issue, index) => (
              <IssueCard
                key={index}
                issue={issue}
                index={index}
                repoUrl={repoUrl}
                issueStatus={issueStatuses?.[`synthesis_low:${index}`]}
                onStatusChange={onIssueStatusChange
                  ? (status) => onIssueStatusChange('synthesis_low', index, status)
                  : undefined
                }
              />
            ))}
          </AccordionDetails>
        </Accordion>
      )}

      {/* Total Effort Estimate */}
      {data.estimated_total_effort_days && (
        <Alert severity="info" sx={{ mt: 3 }}>
          <Typography variant="body1">
            <strong>Estimated Total Effort:</strong> {data.estimated_total_effort_days} days
          </Typography>
        </Alert>
      )}
    </Box>
  );
};

/**
 * SynthesisSection -- top-level component for the "Synthesis Report" tab.
 * Handles both structured and raw/unparsed synthesis data.
 */
const SynthesisSection = ({ synthesis, issueStatuses, repoUrl, onIssueStatusChange }) => {
  if (!synthesis || synthesis.error) {
    return (
      <Alert severity="warning">
        <Typography>
          Synthesis report not available: {synthesis?.error || 'Unknown error'}
        </Typography>
      </Alert>
    );
  }

  // Detect raw JSON/markdown mistakenly stored as a string field
  const looksLikeRawJson = (str) =>
    typeof str === 'string' &&
    (str.trimStart().startsWith('{') || str.trimStart().startsWith('```'));

  // If executive_summary contains raw LLM response, try to recover structured data
  let data = synthesis;
  if (data.executive_summary && looksLikeRawJson(data.executive_summary)) {
    const raw = data.executive_summary;
    // Strip markdown code fences (closing fence may be missing if truncated)
    let text = raw;
    const fenceMatch = text.match(/```(?:json)?\s*\n?([\s\S]*?)(?:\n?\s*```|$)/);
    if (fenceMatch) text = fenceMatch[1];

    const startIdx = text.indexOf('{');
    if (startIdx !== -1) {
      try {
        const parsed = JSON.parse(text.slice(startIdx));
        if (parsed && typeof parsed === 'object' && parsed.executive_summary) {
          data = parsed;
        }
      } catch {
        // JSON likely truncated -- extract the executive_summary value via regex
        const match = text.match(/"executive_summary"\s*:\s*"((?:[^"\\]|\\.)*)"/);
        if (match) {
          try {
            data = { ...data, executive_summary: JSON.parse('"' + match[1] + '"') };
          } catch {
            // leave as-is
          }
        }
      }
    }
  }

  // Check if we have structured data (using the normalised `data`)
  const hasStructuredData =
    (data.executive_summary && !looksLikeRawJson(data.executive_summary)) ||
    data.critical_issues?.length > 0 ||
    data.high_priority?.length > 0 ||
    data.medium_priority?.length > 0 ||
    data.low_priority?.length > 0 ||
    data.quick_wins?.length > 0;

  if (hasStructuredData) {
    return <ParsedSynthesis data={data} issueStatuses={issueStatuses} repoUrl={repoUrl} onIssueStatusChange={onIssueStatusChange} />;
  }

  // Fallback: try to parse from raw_analysis or raw content
  let parsedData = null;
  const rawContent =
    data.raw_analysis ||
    (typeof data === 'string'
      ? data
      : JSON.stringify(data, null, 2));

  try {
    parsedData = JSON.parse(rawContent);
  } catch {
    const jsonMatch = rawContent.match(/```(?:json)?\s*\n?([\s\S]*?)\n?```/);
    if (jsonMatch) {
      try {
        parsedData = JSON.parse(jsonMatch[1]);
      } catch (e) {
        // intentionally ignored
      }
    }
  }

  if (
    parsedData &&
    ((parsedData.executive_summary && !looksLikeRawJson(parsedData.executive_summary)) ||
      parsedData.critical_issues?.length > 0 ||
      parsedData.high_priority?.length > 0)
  ) {
    return <ParsedSynthesis data={parsedData} issueStatuses={issueStatuses} repoUrl={repoUrl} onIssueStatusChange={onIssueStatusChange} />;
  }

  // Markdown fallback -- prefer the original raw LLM text when available
  const markdownContent =
    data.raw_analysis ||
    (synthesis.executive_summary && looksLikeRawJson(synthesis.executive_summary)
      ? synthesis.executive_summary
      : rawContent);

  return (
    <Paper sx={{ p: 3 }}>
      <Alert severity="warning" sx={{ mb: 2 }}>
        <Typography variant="body2">
          <InfoIcon fontSize="small" sx={{ verticalAlign: 'middle', mr: 1 }} />
          Unable to parse structured report. Showing raw AI response:
        </Typography>
      </Alert>
      <Box sx={markdownSx}>
        <ReactMarkdown remarkPlugins={[remarkGfm]}>
          {markdownContent}
        </ReactMarkdown>
      </Box>
    </Paper>
  );
};

export default SynthesisSection;
