import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import store from './store'
import 'bootstrap/dist/css/bootstrap.css'
import 'bootstrap/dist/js/bootstrap.bundle.js'
import axios from 'axios'

const app = createApp(App)
  .use(store)
  .use(router)

// Create a simple toast plugin
app.config.globalProperties.$toast = {
  success(message) {
    this._showToast(message, 'success');
  },
  error(message) {
    this._showToast(message, 'danger');
  },
  _showToast(message, type) {
    const toastContainer = document.getElementById('toast-container') || this._createToastContainer();
    const toast = document.createElement('div');
    toast.className = `toast show bg-${type} text-white`;
    toast.setAttribute('role', 'alert');
    toast.setAttribute('aria-live', 'assertive');
    toast.setAttribute('aria-atomic', 'true');
    
    toast.innerHTML = `
      <div class="toast-body">
        ${message}
        <button type="button" class="btn-close btn-close-white float-end" data-bs-dismiss="toast"></button>
      </div>
    `;
    
    toastContainer.appendChild(toast);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
      toast.remove();
    }, 5000);
    
    // Add click listener to close button
    const closeBtn = toast.querySelector('.btn-close');
    if (closeBtn) {
      closeBtn.addEventListener('click', () => toast.remove());
    }
  },
  _createToastContainer() {
    const container = document.createElement('div');
    container.id = 'toast-container';
    container.className = 'toast-container position-fixed top-0 end-0 p-3';
    container.style.zIndex = '1080';
    document.body.appendChild(container);
    return container;
  }
}

axios.defaults.baseURL = 'http://localhost:8000/api'

axios.interceptors.request.use(
  config => {
    if (store.getters.isAuthenticated) {
      config.headers.Authorization = `Bearer ${store.getters.getAuthToken}`
    }
    return config
  },
  error => Promise.reject(error)
)

axios.interceptors.response.use(
  response => response,
  async error => {
    const originalRequest = error.config
    if (error.response && error.response.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true
      try {
        await store.dispatch('refreshToken')
        const token = store.getters.getAuthToken
        axios.defaults.headers.common['Authorization'] = `Bearer ${token}`
        originalRequest.headers['Authorization'] = `Bearer ${token}`
        return axios(originalRequest)
      } catch (err) {
        store.commit('clearAuth')
        router.push({ name: 'login' })
        return Promise.reject(err)
      }
    }
    return Promise.reject(error)
  }
)

app.mount('#app')
