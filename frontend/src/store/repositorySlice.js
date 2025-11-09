import { createSlice } from '@reduxjs/toolkit';

const initialState = {
  repositories: [],
  currentRepository: null,
  loading: false,
  error: null,
};

const repositorySlice = createSlice({
  name: 'repositories',
  initialState,
  reducers: {
    setRepositories: (state, action) => {
      state.repositories = action.payload;
    },
    addRepository: (state, action) => {
      state.repositories.unshift(action.payload);
    },
    setCurrentRepository: (state, action) => {
      state.currentRepository = action.payload;
    },
    removeRepository: (state, action) => {
      state.repositories = state.repositories.filter(
        repo => repo.id !== action.payload
      );
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
  setRepositories,
  addRepository,
  setCurrentRepository,
  removeRepository,
  setLoading,
  setError,
} = repositorySlice.actions;

export default repositorySlice.reducer;
