import { createSlice } from '@reduxjs/toolkit';

const initialState = {
  analyses: [],
  currentAnalysis: null,
  loading: false,
  error: null,
};

const analysisSlice = createSlice({
  name: 'analyses',
  initialState,
  reducers: {
    setAnalyses: (state, action) => {
      state.analyses = action.payload;
    },
    addAnalysis: (state, action) => {
      state.analyses.unshift(action.payload);
    },
    updateAnalysis: (state, action) => {
      const index = state.analyses.findIndex(a => a.id === action.payload.id);
      if (index !== -1) {
        state.analyses[index] = action.payload;
      }
      if (state.currentAnalysis?.id === action.payload.id) {
        state.currentAnalysis = action.payload;
      }
    },
    setCurrentAnalysis: (state, action) => {
      state.currentAnalysis = action.payload;
    },
    setLoading: (state, action) => {
      state.loading = action.payload;
    },
    setError: (state, action) => {
      state.error = action.payload;
    },
  },
});

export const {
  setAnalyses,
  addAnalysis,
  updateAnalysis,
  setCurrentAnalysis,
  setLoading,
  setError,
} = analysisSlice.actions;

export default analysisSlice.reducer;
