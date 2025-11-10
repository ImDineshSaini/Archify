import { createTheme } from '@mui/material/styles';

// Professional Enterprise Theme - Clean, Conservative, Data-Focused
const theme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#0052CC',
      light: '#4C9AFF',
      dark: '#003C8F',
      contrastText: '#FFFFFF',
    },
    secondary: {
      main: '#6B778C',
      light: '#97A0AF',
      dark: '#505F79',
      contrastText: '#FFFFFF',
    },
    success: {
      main: '#00875A',
      light: '#36B37E',
      dark: '#006644',
    },
    error: {
      main: '#DE350B',
      light: '#FF5630',
      dark: '#BF2600',
    },
    warning: {
      main: '#FF991F',
      light: '#FFAB00',
      dark: '#FF8B00',
    },
    info: {
      main: '#0065FF',
      light: '#4C9AFF',
      dark: '#0052CC',
    },
    background: {
      default: '#F4F5F7',
      paper: '#FFFFFF',
    },
    text: {
      primary: '#172B4D',
      secondary: '#5E6C84',
      disabled: '#A5ADBA',
    },
    divider: '#DFE1E6',
  },
  typography: {
    fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", "Roboto", "Oxygen", "Ubuntu", "Fira Sans", "Droid Sans", "Helvetica Neue", sans-serif',
    h1: {
      fontSize: '2.25rem',
      fontWeight: 600,
      lineHeight: 1.2,
      color: '#172B4D',
    },
    h2: {
      fontSize: '1.875rem',
      fontWeight: 600,
      lineHeight: 1.3,
      color: '#172B4D',
    },
    h3: {
      fontSize: '1.5rem',
      fontWeight: 600,
      lineHeight: 1.3,
      color: '#172B4D',
    },
    h4: {
      fontSize: '1.25rem',
      fontWeight: 600,
      lineHeight: 1.4,
      color: '#172B4D',
    },
    h5: {
      fontSize: '1.125rem',
      fontWeight: 600,
      lineHeight: 1.4,
      color: '#172B4D',
    },
    h6: {
      fontSize: '1rem',
      fontWeight: 600,
      lineHeight: 1.5,
      color: '#172B4D',
    },
    body1: {
      fontSize: '0.875rem',
      lineHeight: 1.5,
      color: '#172B4D',
    },
    body2: {
      fontSize: '0.8125rem',
      lineHeight: 1.5,
      color: '#5E6C84',
    },
    button: {
      textTransform: 'none',
      fontWeight: 500,
      fontSize: '0.875rem',
    },
  },
  shape: {
    borderRadius: 3,
  },
  shadows: [
    'none',
    '0 1px 1px rgba(9, 30, 66, 0.25), 0 0 1px rgba(9, 30, 66, 0.31)',
    '0 2px 4px rgba(9, 30, 66, 0.2), 0 0 1px rgba(9, 30, 66, 0.31)',
    '0 3px 5px rgba(9, 30, 66, 0.2), 0 0 1px rgba(9, 30, 66, 0.31)',
    '0 4px 8px rgba(9, 30, 66, 0.15), 0 0 1px rgba(9, 30, 66, 0.31)',
    '0 5px 10px rgba(9, 30, 66, 0.15), 0 0 1px rgba(9, 30, 66, 0.31)',
    '0 8px 16px rgba(9, 30, 66, 0.15), 0 0 1px rgba(9, 30, 66, 0.31)',
    '0 10px 18px rgba(9, 30, 66, 0.15), 0 0 1px rgba(9, 30, 66, 0.31)',
    '0 12px 20px rgba(9, 30, 66, 0.15), 0 0 1px rgba(9, 30, 66, 0.31)',
    '0 14px 22px rgba(9, 30, 66, 0.15), 0 0 1px rgba(9, 30, 66, 0.31)',
    '0 16px 24px rgba(9, 30, 66, 0.15), 0 0 1px rgba(9, 30, 66, 0.31)',
    '0 18px 26px rgba(9, 30, 66, 0.15), 0 0 1px rgba(9, 30, 66, 0.31)',
    '0 20px 28px rgba(9, 30, 66, 0.15), 0 0 1px rgba(9, 30, 66, 0.31)',
    '0 22px 30px rgba(9, 30, 66, 0.15), 0 0 1px rgba(9, 30, 66, 0.31)',
    '0 24px 32px rgba(9, 30, 66, 0.15), 0 0 1px rgba(9, 30, 66, 0.31)',
    '0 26px 34px rgba(9, 30, 66, 0.15), 0 0 1px rgba(9, 30, 66, 0.31)',
    '0 28px 36px rgba(9, 30, 66, 0.15), 0 0 1px rgba(9, 30, 66, 0.31)',
    '0 30px 38px rgba(9, 30, 66, 0.15), 0 0 1px rgba(9, 30, 66, 0.31)',
    '0 32px 40px rgba(9, 30, 66, 0.15), 0 0 1px rgba(9, 30, 66, 0.31)',
    '0 34px 42px rgba(9, 30, 66, 0.15), 0 0 1px rgba(9, 30, 66, 0.31)',
    '0 36px 44px rgba(9, 30, 66, 0.15), 0 0 1px rgba(9, 30, 66, 0.31)',
    '0 38px 46px rgba(9, 30, 66, 0.15), 0 0 1px rgba(9, 30, 66, 0.31)',
    '0 40px 48px rgba(9, 30, 66, 0.15), 0 0 1px rgba(9, 30, 66, 0.31)',
    '0 42px 50px rgba(9, 30, 66, 0.15), 0 0 1px rgba(9, 30, 66, 0.31)',
    '0 44px 52px rgba(9, 30, 66, 0.15), 0 0 1px rgba(9, 30, 66, 0.31)',
  ],
  components: {
    MuiCssBaseline: {
      styleOverrides: {
        body: {
          scrollbarColor: '#C1C7D0 #F4F5F7',
          '&::-webkit-scrollbar': {
            width: 8,
            height: 8,
          },
          '&::-webkit-scrollbar-thumb': {
            backgroundColor: '#C1C7D0',
            borderRadius: 4,
          },
          '&::-webkit-scrollbar-thumb:hover': {
            backgroundColor: '#A5ADBA',
          },
          '&::-webkit-scrollbar-track': {
            backgroundColor: '#F4F5F7',
          },
        },
      },
    },
    MuiButton: {
      styleOverrides: {
        root: {
          textTransform: 'none',
          fontWeight: 500,
          borderRadius: 3,
          padding: '8px 16px',
          fontSize: '0.875rem',
          boxShadow: 'none',
          '&:hover': {
            boxShadow: 'none',
          },
        },
        contained: {
          boxShadow: 'none',
          '&:hover': {
            boxShadow: '0 2px 4px rgba(9, 30, 66, 0.2)',
          },
          '&:active': {
            boxShadow: 'none',
          },
        },
        containedPrimary: {
          backgroundColor: '#0052CC',
          '&:hover': {
            backgroundColor: '#0065FF',
          },
        },
        outlined: {
          borderWidth: 1,
          '&:hover': {
            borderWidth: 1,
          },
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          boxShadow: '0 1px 1px rgba(9, 30, 66, 0.25), 0 0 1px rgba(9, 30, 66, 0.31)',
          borderRadius: 3,
          border: '1px solid #DFE1E6',
          '&:hover': {
            boxShadow: '0 4px 8px rgba(9, 30, 66, 0.15), 0 0 1px rgba(9, 30, 66, 0.31)',
          },
        },
      },
    },
    MuiPaper: {
      styleOverrides: {
        root: {
          backgroundImage: 'none',
        },
        elevation0: {
          boxShadow: 'none',
        },
        elevation1: {
          boxShadow: '0 1px 1px rgba(9, 30, 66, 0.25), 0 0 1px rgba(9, 30, 66, 0.31)',
        },
        elevation2: {
          boxShadow: '0 2px 4px rgba(9, 30, 66, 0.2), 0 0 1px rgba(9, 30, 66, 0.31)',
        },
        elevation3: {
          boxShadow: '0 4px 8px rgba(9, 30, 66, 0.15), 0 0 1px rgba(9, 30, 66, 0.31)',
        },
      },
    },
    MuiAppBar: {
      styleOverrides: {
        root: {
          backgroundColor: '#0052CC',
          boxShadow: '0 2px 4px rgba(9, 30, 66, 0.2)',
        },
        colorPrimary: {
          backgroundColor: '#0052CC',
        },
      },
    },
    MuiDrawer: {
      styleOverrides: {
        paper: {
          backgroundColor: '#FFFFFF',
          borderRight: '1px solid #DFE1E6',
        },
      },
    },
    MuiListItemButton: {
      styleOverrides: {
        root: {
          borderRadius: 3,
          margin: '2px 8px',
          padding: '8px 12px',
          '&:hover': {
            backgroundColor: '#F4F5F7',
          },
          '&.Mui-selected': {
            backgroundColor: '#DEEBFF',
            borderLeft: '3px solid #0052CC',
            '&:hover': {
              backgroundColor: '#B3D4FF',
            },
          },
        },
      },
    },
    MuiChip: {
      styleOverrides: {
        root: {
          fontWeight: 500,
          borderRadius: 3,
          height: 24,
          fontSize: '0.75rem',
        },
        filled: {
          boxShadow: 'none',
        },
      },
    },
    MuiAlert: {
      styleOverrides: {
        root: {
          borderRadius: 3,
          border: '1px solid',
        },
        standardInfo: {
          backgroundColor: '#DEEBFF',
          borderColor: '#B3D4FF',
          color: '#0747A6',
        },
        standardSuccess: {
          backgroundColor: '#E3FCEF',
          borderColor: '#ABF5D1',
          color: '#006644',
        },
        standardWarning: {
          backgroundColor: '#FFFAE6',
          borderColor: '#FFF0B3',
          color: '#974F0C',
        },
        standardError: {
          backgroundColor: '#FFEBE6',
          borderColor: '#FFBDAD',
          color: '#BF2600',
        },
      },
    },
    MuiTextField: {
      styleOverrides: {
        root: {
          '& .MuiOutlinedInput-root': {
            borderRadius: 3,
            '& fieldset': {
              borderColor: '#DFE1E6',
            },
            '&:hover fieldset': {
              borderColor: '#B3BAC5',
            },
            '&.Mui-focused fieldset': {
              borderWidth: 2,
              borderColor: '#0052CC',
            },
          },
        },
      },
    },
    MuiTableCell: {
      styleOverrides: {
        head: {
          fontWeight: 600,
          backgroundColor: '#F4F5F7',
          color: '#172B4D',
          borderBottom: '2px solid #DFE1E6',
          fontSize: '0.75rem',
          textTransform: 'uppercase',
          letterSpacing: '0.5px',
        },
        root: {
          borderBottom: '1px solid #EBECF0',
          fontSize: '0.875rem',
          padding: '12px 16px',
        },
      },
    },
    MuiTab: {
      styleOverrides: {
        root: {
          textTransform: 'none',
          fontWeight: 500,
          fontSize: '0.875rem',
          minHeight: 48,
          color: '#5E6C84',
          '&:hover': {
            color: '#172B4D',
          },
          '&.Mui-selected': {
            color: '#0052CC',
            fontWeight: 600,
          },
        },
      },
    },
    MuiTabs: {
      styleOverrides: {
        root: {
          borderBottom: '2px solid #DFE1E6',
        },
        indicator: {
          height: 3,
          backgroundColor: '#0052CC',
        },
      },
    },
    MuiTooltip: {
      styleOverrides: {
        tooltip: {
          backgroundColor: '#172B4D',
          fontSize: '0.75rem',
          fontWeight: 400,
          borderRadius: 3,
          padding: '6px 10px',
        },
      },
    },
    MuiAccordion: {
      styleOverrides: {
        root: {
          border: '1px solid #DFE1E6',
          boxShadow: 'none',
          '&:before': {
            display: 'none',
          },
          '&.Mui-expanded': {
            margin: 0,
          },
        },
      },
    },
    MuiAccordionSummary: {
      styleOverrides: {
        root: {
          backgroundColor: '#FAFBFC',
          borderBottom: '1px solid #DFE1E6',
          '&:hover': {
            backgroundColor: '#F4F5F7',
          },
        },
      },
    },
  },
});

export default theme;
