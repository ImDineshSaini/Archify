import { configureStore } from '@reduxjs/toolkit';
import authReducer from './authSlice';
import repositoryReducer from './repositorySlice';
import analysisReducer from './analysisSlice';

export const store = configureStore({
  reducer: {
    auth: authReducer,
    repositories: repositoryReducer,
    analyses: analysisReducer,
  },
});
