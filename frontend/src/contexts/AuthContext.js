import React, { createContext, useContext, useState, useEffect } from 'react';
import axios from 'axios';
import toast from 'react-hot-toast';

const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

const API_URL = process.env.REACT_APP_BACKEND_URL;

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [token, setToken] = useState(localStorage.getItem('token'));

  // Set axios default headers
  useEffect(() => {
    if (token) {
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
    } else {
      delete axios.defaults.headers.common['Authorization'];
    }
  }, [token]);

  // Load user on mount
  useEffect(() => {
    const loadUser = async () => {
      if (token) {
        try {
          const response = await axios.get(`${API_URL}/api/auth/me`);
          setUser(response.data);
        } catch (error) {
          console.error('Failed to load user:', error);
          localStorage.removeItem('token');
          setToken(null);
        }
      }
      setLoading(false);
    };

    loadUser();
  }, [token]);

  const login = async (email, password) => {
    try {
      // Set axios timeout for production issues
      const response = await axios.post(`${API_URL}/api/auth/login`, {
        email,
        password,
      }, {
        timeout: 30000, // 30 second timeout
        headers: {
          'Content-Type': 'application/json'
        }
      });

      const { access_token, user: userData } = response.data;
      
      localStorage.setItem('token', access_token);
      setToken(access_token);
      setUser(userData);
      
      toast.success(`Welcome back, ${userData.username}!`);
      return { success: true };
    } catch (error) {
      console.error('Login error:', error);
      
      // Enhanced error handling for timeout issues
      if (error.code === 'ECONNABORTED') {
        toast.error('Connection timeout. Please try again.');
      } else if (error.response?.status === 401) {
        toast.error('Invalid credentials');
      } else if (error.response?.status === 400) {
        toast.error(error.response?.data?.detail || 'Invalid request');
      } else {
        toast.error('Login failed. Please check your connection.');
      }
      
      return { success: false, error: error.message };
    }
  };

  const register = async (userData) => {
    try {
      // Set axios timeout for production issues
      const response = await axios.post(`${API_URL}/api/auth/register`, userData, {
        timeout: 30000, // 30 second timeout
        headers: {
          'Content-Type': 'application/json'
        }
      });
      
      const { access_token, user: newUser } = response.data;
      
      localStorage.setItem('token', access_token);
      setToken(access_token);
      setUser(newUser);
      
      toast.success(`Welcome to IDFS PathwayIQ™, ${newUser.username}!`);
      return { success: true };
    } catch (error) {
      console.error('Registration error:', error);
      
      // Enhanced error handling for timeout issues
      if (error.code === 'ECONNABORTED') {
        toast.error('Connection timeout. Please try again.');
      } else if (error.response?.status === 400) {
        toast.error(error.response?.data?.detail || 'Registration failed');
      } else if (error.response?.status === 409) {
        toast.error('User already exists');
      } else {
        toast.error('Registration failed. Please check your connection.');
      }
      
      return { success: false, error: error.message };
    }
  };

  const logout = () => {
    localStorage.removeItem('token');
    setToken(null);
    setUser(null);
    delete axios.defaults.headers.common['Authorization'];
    toast.success('Logged out successfully');
  };

  const updateUser = (userData) => {
    setUser(prev => ({ ...prev, ...userData }));
  };

  const value = {
    user,
    token,
    loading,
    login,
    register,
    logout,
    updateUser,
    isAuthenticated: !!token && !!user,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};