import { useState, useEffect } from 'react';
import {
  Container,
  Typography,
  Box,
  Paper,
  TextField,
  Button,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Alert,
  Tabs,
  Tab,
  Divider,
} from '@mui/material';
import { settingsAPI } from '../services/api';

function TabPanel({ children, value, index }) {
  return (
    <div hidden={value !== index}>
      {value === index && <Box sx={{ py: 3 }}>{children}</Box>}
    </div>
  );
}

export default function Settings() {
  const [tabValue, setTabValue] = useState(0);
  const [llmConfig, setLlmConfig] = useState({
    provider: 'claude',
    api_key: '',
    model: '',
    endpoint: '',
    deployment_name: '',
  });
  const [gitConfig, setGitConfig] = useState({
    source: 'github',
    token: '',
  });
  const [success, setSuccess] = useState('');
  const [error, setError] = useState('');
  const [currentProvider, setCurrentProvider] = useState('');

  useEffect(() => {
    fetchCurrentProvider();
  }, []);

  const fetchCurrentProvider = async () => {
    try {
      const response = await settingsAPI.getCurrentLLM();
      setCurrentProvider(response.data.provider);
    } catch (error) {
      console.error('Error fetching current provider:', error);
    }
  };

  const handleTabChange = (event, newValue) => {
    setTabValue(newValue);
    setSuccess('');
    setError('');
  };

  const handleLlmChange = (e) => {
    setLlmConfig({ ...llmConfig, [e.target.name]: e.target.value });
  };

  const handleGitChange = (e) => {
    setGitConfig({ ...gitConfig, [e.target.name]: e.target.value });
  };

  const handleSaveLlm = async () => {
    setError('');
    setSuccess('');

    try {
      const configToSubmit = {
        provider: llmConfig.provider,
        api_key: llmConfig.api_key,
      };

      if (llmConfig.provider === 'azure') {
        configToSubmit.endpoint = llmConfig.endpoint;
        configToSubmit.deployment_name = llmConfig.deployment_name;
      }

      if (llmConfig.model) {
        configToSubmit.model = llmConfig.model;
      }

      await settingsAPI.configureLLM(configToSubmit);
      setSuccess('LLM provider configured successfully');
      setLlmConfig({
        provider: 'claude',
        api_key: '',
        model: '',
        endpoint: '',
        deployment_name: '',
      });
      fetchCurrentProvider();
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to configure LLM provider');
    }
  };

  const handleSaveGit = async () => {
    setError('');
    setSuccess('');

    try {
      await settingsAPI.configureGit(gitConfig);
      setSuccess(`${gitConfig.source} token configured successfully`);
      setGitConfig({ source: 'github', token: '' });
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to configure Git token');
    }
  };

  return (
    <Container maxWidth="md">
      <Typography variant="h4" gutterBottom>
        Settings
      </Typography>

      <Paper sx={{ mt: 3 }}>
        <Tabs value={tabValue} onChange={handleTabChange}>
          <Tab label="LLM Provider" />
          <Tab label="Git Integration" />
        </Tabs>

        <Divider />

        {/* LLM Provider Tab */}
        <TabPanel value={tabValue} index={0}>
          {success && (
            <Alert severity="success" sx={{ mb: 2 }}>
              {success}
            </Alert>
          )}
          {error && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {error}
            </Alert>
          )}

          {currentProvider && currentProvider !== 'not_configured' && (
            <Alert severity="info" sx={{ mb: 2 }}>
              Current provider: {currentProvider}
            </Alert>
          )}

          <Box component="form" sx={{ px: 2 }}>
            <FormControl fullWidth sx={{ mb: 3 }}>
              <InputLabel>Provider</InputLabel>
              <Select
                name="provider"
                value={llmConfig.provider}
                label="Provider"
                onChange={handleLlmChange}
              >
                <MenuItem value="claude">Claude (Anthropic)</MenuItem>
                <MenuItem value="openai">OpenAI</MenuItem>
                <MenuItem value="azure">Azure OpenAI</MenuItem>
              </Select>
            </FormControl>

            <TextField
              fullWidth
              label="API Key"
              name="api_key"
              type="password"
              value={llmConfig.api_key}
              onChange={handleLlmChange}
              sx={{ mb: 3 }}
              required
            />

            <TextField
              fullWidth
              label="Model (Optional)"
              name="model"
              value={llmConfig.model}
              onChange={handleLlmChange}
              helperText="Leave empty for default model"
              sx={{ mb: 3 }}
            />

            {llmConfig.provider === 'azure' && (
              <>
                <TextField
                  fullWidth
                  label="Azure Endpoint"
                  name="endpoint"
                  value={llmConfig.endpoint}
                  onChange={handleLlmChange}
                  placeholder="https://your-resource.openai.azure.com"
                  sx={{ mb: 3 }}
                  required
                />

                <TextField
                  fullWidth
                  label="Deployment Name"
                  name="deployment_name"
                  value={llmConfig.deployment_name}
                  onChange={handleLlmChange}
                  sx={{ mb: 3 }}
                  required
                />
              </>
            )}

            <Box display="flex" gap={2}>
              <Button variant="contained" onClick={handleSaveLlm}>
                Save Configuration
              </Button>
            </Box>

            <Box sx={{ mt: 3, p: 2, bgcolor: 'background.default', borderRadius: 1 }}>
              <Typography variant="subtitle2" gutterBottom>
                Configuration Guide:
              </Typography>
              <Typography variant="body2" color="text.secondary">
                • <strong>Claude:</strong> Get your API key from console.anthropic.com
                <br />
                • <strong>OpenAI:</strong> Get your API key from platform.openai.com
                <br />
                • <strong>Azure OpenAI:</strong> Requires endpoint URL and deployment name from Azure Portal
              </Typography>
            </Box>
          </Box>
        </TabPanel>

        {/* Git Integration Tab */}
        <TabPanel value={tabValue} index={1}>
          {success && (
            <Alert severity="success" sx={{ mb: 2 }}>
              {success}
            </Alert>
          )}
          {error && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {error}
            </Alert>
          )}

          <Box component="form" sx={{ px: 2 }}>
            <FormControl fullWidth sx={{ mb: 3 }}>
              <InputLabel>Git Provider</InputLabel>
              <Select
                name="source"
                value={gitConfig.source}
                label="Git Provider"
                onChange={handleGitChange}
              >
                <MenuItem value="github">GitHub</MenuItem>
                <MenuItem value="gitlab">GitLab</MenuItem>
              </Select>
            </FormControl>

            <TextField
              fullWidth
              label="Access Token"
              name="token"
              type="password"
              value={gitConfig.token}
              onChange={handleGitChange}
              helperText="Required for accessing private repositories"
              sx={{ mb: 3 }}
              required
            />

            <Button variant="contained" onClick={handleSaveGit}>
              Save Token
            </Button>

            <Box sx={{ mt: 3, p: 2, bgcolor: 'background.default', borderRadius: 1 }}>
              <Typography variant="subtitle2" gutterBottom>
                How to generate tokens:
              </Typography>
              <Typography variant="body2" color="text.secondary">
                • <strong>GitHub:</strong> Settings → Developer settings → Personal access tokens → Generate new token
                <br />
                • <strong>GitLab:</strong> Preferences → Access Tokens → Add new token
                <br />
                <br />
                Required scopes: repo (GitHub) or read_repository (GitLab)
              </Typography>
            </Box>
          </Box>
        </TabPanel>
      </Paper>
    </Container>
  );
}
