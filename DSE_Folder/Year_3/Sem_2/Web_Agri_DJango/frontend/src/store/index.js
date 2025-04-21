import { createStore } from 'vuex'
import axios from 'axios'

const API_URL = 'http://localhost:8000/api'

export default createStore({
  state: {
    files: [],
    currentFile: null,
    processedData: [],
    loading: false,
    error: null,
    // Authentication state
    token: localStorage.getItem('token') || null,
    refreshToken: localStorage.getItem('refreshToken') || null,
    user: JSON.parse(localStorage.getItem('user')) || null,
    isAuthenticated: !!localStorage.getItem('token')
  },
  getters: {
    isAuthenticated: state => state.isAuthenticated,
    currentUser: state => state.user,
    getAuthToken: state => state.token,
    getFiles: state => state.files,
    getCurrentFile: state => state.currentFile,
    getProcessedData: state => state.processedData,
    isLoading: state => state.loading,
    getError: state => state.error
  },
  mutations: {
    setFiles(state, files) {
      state.files = files
    },
    setCurrentFile(state, file) {
      state.currentFile = file
    },
    setProcessedData(state, data) {
      state.processedData = data
    },
    setLoading(state, loading) {
      state.loading = loading
    },
    setError(state, error) {
      state.error = error
    },
    // Authentication mutations
    setAuth(state, { token, refreshToken, user }) {
      state.token = token
      state.refreshToken = refreshToken
      state.user = user
      state.isAuthenticated = true
      
      // Store in localStorage
      localStorage.setItem('token', token)
      localStorage.setItem('refreshToken', refreshToken)
      localStorage.setItem('user', JSON.stringify(user))
    },
    clearAuth(state) {
      state.token = null
      state.refreshToken = null
      state.user = null
      state.isAuthenticated = false
      
      // Clear localStorage
      localStorage.removeItem('token')
      localStorage.removeItem('refreshToken')
      localStorage.removeItem('user')
    }
  },
  actions: {
    // Authentication actions
    registerUser({ commit }, userData) {
      commit('setLoading', true)
      commit('setError', null)
      
      return axios.post(`${API_URL}/auth/register/`, userData)
        .then(response => {
          const { access, refresh, user } = response.data
          commit('setAuth', { 
            token: access, 
            refreshToken: refresh, 
            user 
          })
          return response
        })
        .catch(error => {
          commit('setError', error.response?.data || 'Registration failed')
          throw error
        })
        .finally(() => {
          commit('setLoading', false)
        })
    },
    
    loginUser({ commit }, credentials) {
      commit('setLoading', true)
      commit('setError', null)
      
      return axios.post(`${API_URL}/auth/login/`, credentials)
        .then(response => {
          const { access, refresh, user } = response.data
          commit('setAuth', { 
            token: access, 
            refreshToken: refresh, 
            user 
          })
          return response
        })
        .catch(error => {
          commit('setError', error.response?.data || 'Login failed')
          throw error
        })
        .finally(() => {
          commit('setLoading', false)
        })
    },
    
    refreshToken({ commit, state }) {
      if (!state.refreshToken) {
        return Promise.reject(new Error('No refresh token available'))
      }
      
      return axios.post(`${API_URL}/auth/token/refresh/`, {
        refresh: state.refreshToken
      })
        .then(response => {
          const { access } = response.data
          
          // Update only the access token
          commit('setAuth', { 
            token: access, 
            refreshToken: state.refreshToken, 
            user: state.user 
          })
          
          return response
        })
        .catch(error => {
          // If refresh token is invalid, log the user out
          commit('clearAuth')
          throw error
        })
    },
    
    logout({ commit }) {
      commit('clearAuth')
      return Promise.resolve()
    },
    
    // File management actions
    fetchFiles({ commit, getters }) {
      commit('setLoading', true)
      commit('setError', null)
      
      const headers = getters.isAuthenticated ? { Authorization: `Bearer ${getters.getAuthToken}` } : {}
      
      return axios.get(`${API_URL}/excel-files/`, { headers })
        .then(response => {
          commit('setFiles', response.data)
          return response.data
        })
        .catch(error => {
          commit('setError', error.response?.data || 'Failed to fetch files')
          throw error
        })
        .finally(() => {
          commit('setLoading', false)
        })
    },
    
    fetchFile({ commit, getters }, fileId) {
      commit('setLoading', true)
      commit('setError', null)
      
      const headers = getters.isAuthenticated ? { Authorization: `Bearer ${getters.getAuthToken}` } : {}
      
      return axios.get(`${API_URL}/excel-files/${fileId}/`, { headers })
        .then(response => {
          commit('setCurrentFile', response.data)
          return response.data
        })
        .catch(error => {
          commit('setError', error.response?.data || 'Failed to fetch file details')
          throw error
        })
        .finally(() => {
          commit('setLoading', false)
        })
    },
    
    uploadFile({ commit, getters }, { title, file }) {
      commit('setLoading', true)
      commit('setError', null)
      
      const formData = new FormData()
      formData.append('title', title)
      formData.append('file', file)
      
      const headers = { 
        'Content-Type': 'multipart/form-data',
        ...(getters.isAuthenticated ? { Authorization: `Bearer ${getters.getAuthToken}` } : {})
      }
      
      return axios.post(`${API_URL}/excel-files/`, formData, { headers })
        .then(response => {
          return response.data
        })
        .catch(error => {
          commit('setError', error.response?.data || 'Failed to upload file')
          throw error
        })
        .finally(() => {
          commit('setLoading', false)
        })
    },
    
    processFile({ commit, getters }, fileId) {
      commit('setLoading', true)
      commit('setError', null)
      
      const headers = getters.isAuthenticated ? { Authorization: `Bearer ${getters.getAuthToken}` } : {}
      
      return axios.post(`${API_URL}/excel-files/${fileId}/process/`, {}, { headers })
        .then(response => {
          return response.data
        })
        .catch(error => {
          commit('setError', error.response?.data || 'Failed to process file')
          throw error
        })
        .finally(() => {
          commit('setLoading', false)
        })
    },
    
    fetchProcessedData({ commit, getters }, fileId) {
      commit('setLoading', true)
      commit('setError', null)
      
      const headers = getters.isAuthenticated ? { Authorization: `Bearer ${getters.getAuthToken}` } : {}
      
      return axios.get(`${API_URL}/processed-data/by_file/?file_id=${fileId}`, { headers })
        .then(response => {
          commit('setProcessedData', response.data)
          return response.data
        })
        .catch(error => {
          commit('setError', error.response?.data || 'Failed to fetch processed data')
          throw error
        })
        .finally(() => {
          commit('setLoading', false)
        })
    }
  }
})
