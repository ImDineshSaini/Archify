import {
  Typography,
  Box,
  Chip,
  Accordion,
  AccordionSummary,
  AccordionDetails,
} from '@mui/material';
import {
  ExpandMore,
  TrendingUp,
  CheckCircle,
  Security,
  Build,
  Search,
} from '@mui/icons-material';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';
import { getScoreColor, getScoreGrade } from '../../utils/statusColors';

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

/**
 * Build the metric definitions that include analysis-dependent text.
 */
function buildMetrics(analysis) {
  return [
    {
      title: 'Maintainability',
      score: analysis.maintainability_score || 0,
      icon: <Build />,
      details: `
## What is Maintainability?

Maintainability measures how easy it is to maintain and modify your codebase.

### Key Factors:
- **Code Complexity**: Cyclomatic complexity, nesting depth
- **Code Duplication**: Repeated code patterns
- **Documentation**: Comment coverage and quality
- **Function Size**: Average function length

### Your Score: ${(analysis.maintainability_score || 0).toFixed(1)}/100

${analysis.maintainability_score >= 80 ?
  '**Excellent!** Your code is well-structured and easy to maintain.' :
  analysis.maintainability_score >= 60 ?
  '**Good, but improvable.** Consider refactoring complex functions.' :
  '**Needs work.** High complexity will slow down development.'}

### Recommendations:
1. Break down functions longer than 50 lines
2. Reduce cyclomatic complexity to < 10
3. Eliminate duplicate code blocks
4. Add inline documentation for complex logic
      `,
    },
    {
      title: 'Reliability',
      score: analysis.reliability_score || 0,
      icon: <CheckCircle />,
      details: `
## What is Reliability?

Reliability measures the probability of failure-free operation.

### Key Factors:
- **Error Handling**: Try-catch coverage
- **Test Coverage**: Unit and integration tests
- **Bug Density**: Historical bugs per KLOC
- **Code Stability**: Change frequency

### Your Score: ${(analysis.reliability_score || 0).toFixed(1)}/100

${analysis.reliability_score >= 80 ?
  '**Highly Reliable!** Low risk of production failures.' :
  analysis.reliability_score >= 60 ?
  '**Moderate Risk.** Some areas need error handling.' :
  '**High Risk.** Critical reliability issues detected.'}

### Recommendations:
1. Add error handling to all API calls
2. Implement input validation
3. Increase test coverage to > 80%
4. Add logging for critical operations
      `,
    },
    {
      title: 'Security',
      score: analysis.security_score || 0,
      icon: <Security />,
      details: `
## What is Security?

Security measures protection against vulnerabilities and attacks.

### Key Factors:
- **Vulnerability Scanning**: Known CVEs
- **Input Validation**: SQL injection, XSS prevention
- **Authentication**: Secure auth implementation
- **Dependency Security**: Outdated packages

### Your Score: ${(analysis.security_score || 0).toFixed(1)}/100

${analysis.security_score >= 80 ?
  '**Secure!** No critical vulnerabilities found.' :
  analysis.security_score >= 60 ?
  '**Moderate Risk.** Some security issues detected.' :
  '**Critical Risk!** Immediate security fixes needed.'}

### Recommendations:
1. Update dependencies with known vulnerabilities
2. Implement parameterized queries
3. Add rate limiting to prevent brute force
4. Enable HTTPS and secure headers
      `,
    },
    {
      title: 'Scalability',
      score: analysis.scalability_score || 0,
      icon: <TrendingUp />,
      details: `
## What is Scalability?

Scalability measures the ability to handle growth.

### Key Factors:
- **Algorithm Efficiency**: Big-O complexity
- **Database Design**: Query optimization
- **Caching Strategy**: Response time
- **Architecture**: Monolith vs microservices

### Your Score: ${(analysis.scalability_score || 0).toFixed(1)}/100

${analysis.scalability_score >= 80 ?
  '**Highly Scalable!** Ready for growth.' :
  analysis.scalability_score >= 60 ?
  '**Some Bottlenecks.** Optimization recommended.' :
  '**Scalability Issues.** Will struggle under load.'}

### Recommendations:
1. Implement caching for frequent queries
2. Optimize N+1 database queries
3. Add database indexes
4. Consider horizontal scaling architecture
      `,
    },
  ];
}

/**
 * Detailed Metrics tab (tab 3) – expandable accordion cards for each
 * quality metric with markdown-rendered details and recommendations.
 */
export default function DetailedMetricsTab({ analysis, expandedMetric, setExpandedMetric }) {
  const metrics = buildMetrics(analysis);

  return (
    <>
      <Box display="flex" alignItems="center" sx={{ mb: 2 }}>
        <Search sx={{ mr: 1 }} />
        <Typography variant="h5">
          Detailed Quality Metrics
        </Typography>
      </Box>

      {metrics.map((metric, index) => (
        <Accordion
          key={index}
          expanded={expandedMetric === index}
          onChange={() => setExpandedMetric(expandedMetric === index ? null : index)}
          sx={{ mb: 2 }}
        >
          <AccordionSummary expandIcon={<ExpandMore />}>
            <Box display="flex" alignItems="center" width="100%">
              <Box sx={{ color: getScoreColor(metric.score), mr: 2 }}>
                {metric.icon}
              </Box>
              <Typography variant="h6" sx={{ flexGrow: 1 }}>
                {metric.title}
              </Typography>
              <Chip
                label={`${metric.score.toFixed(1)}/100`}
                sx={{
                  bgcolor: getScoreColor(metric.score),
                  color: 'white',
                  fontWeight: 'bold',
                  mr: 2,
                }}
              />
              <Typography variant="h5" sx={{ color: getScoreColor(metric.score), fontWeight: 'bold' }}>
                {getScoreGrade(metric.score)}
              </Typography>
            </Box>
          </AccordionSummary>
          <AccordionDetails>
            <ReactMarkdown
              remarkPlugins={[remarkGfm]}
              components={markdownComponents}
            >
              {metric.details}
            </ReactMarkdown>
          </AccordionDetails>
        </Accordion>
      ))}
    </>
  );
}
