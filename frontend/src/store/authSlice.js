import { createSlice } from '@reduxjs/toolkit';

const initialState = {
  user: null,
  token: localStorage.getItem('token'),
  isAuthenticated: !!localStorage.getItem('token'),
  isAdmin: JSON.parse(localStorage.getItem('is_admin') || 'false'),
  loading: false,
  error: null,
};

const authSlice = createSlice({
  name: 'auth',
  initialState,
  reducers: {
    loginStart: (state) => {
      state.loading = true;
      state.error = null;
    },
    loginSuccess: (state, action) => {
      state.loading = false;
      state.isAuthenticated = true;
      state.token = action.payload.token;
      state.user = action.payload.user;
      state.isAdmin = action.payload.user?.is_admin || false;
      localStorage.setItem('token', action.payload.token);
      localStorage.setItem('is_admin', JSON.stringify(action.payload.user?.is_admin || false));
    },
    loginFailure: (state, action) => {
      state.loading = false;
      state.error = action.payload;
    },
    logout: (state) => {
      state.user = null;
      state.token = null;
      state.isAuthenticated = false;
      state.isAdmin = false;
      localStorage.removeItem('token');
      localStorage.removeItem('is_admin');
    },
    setUser: (state, action) => {
      state.user = action.payload;
    },
  },
});

export const { loginStart, loginSuccess, loginFailure, logout, setUser } = authSlice.actions;
export default authSlice.reducer;
