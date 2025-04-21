<template>
  <div id="app">
    <nav v-if="isAuthenticated" class="navbar navbar-expand-lg navbar-dark bg-success mb-4">
      <div class="container">
        <router-link class="navbar-brand" to="/">
          <span class="brand-name">Aqua<span class="text-light">Green</span></span>
        </router-link>
        <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
          <span class="navbar-toggler-icon"></span>
        </button>
        <div class="collapse navbar-collapse" id="navbarNav">
          <ul class="navbar-nav me-auto">
            <li class="nav-item">
              <router-link class="nav-link" to="/">Home</router-link>
            </li>
            <li class="nav-item">
              <router-link class="nav-link" to="/upload">Upload</router-link>
            </li>
            <li class="nav-item">
              <router-link class="nav-link" to="/files">Files</router-link>
            </li>
          </ul>
          <div class="d-flex">
            <span class="navbar-text me-3">
              Welcome, {{ currentUser ? currentUser.username : 'User' }}
            </span>
            <button @click="logout" class="btn btn-outline-light btn-sm">Logout</button>
          </div>
        </div>
      </div>
    </nav>

    <div class="container mt-4">
      <div v-if="error" class="alert alert-danger alert-dismissible fade show" role="alert">
        {{ error }}
        <button type="button" class="btn-close" @click="clearError"></button>
      </div>
      <router-view/>
    </div>

    <footer v-if="isAuthenticated" class="footer mt-5 py-3 bg-light">
      <div class="container text-center">
        <span class="text-muted">AquaGreen Greenhouse Management System &copy; {{ new Date().getFullYear() }}</span>
      </div>
    </footer>
  </div>
</template>

<script>
import { mapState, mapActions } from 'vuex';

export default {
  name: 'App',
  computed: {
    ...mapState(['error']),
    isAuthenticated() {
      return this.$store.state.isAuthenticated;
    },
    currentUser() {
      return this.$store.state.user;
    }
  },
  methods: {
    ...mapActions(['logout']),
    clearError() {
      this.$store.commit('setError', null);
    }
  }
}
</script>

<style>
:root {
  --primary-color: #198754;
  --secondary-color: #157347;
  --accent-color: #75b798;
  --light-green: #d1e7dd;
}

body {
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  background-color: #f8f9fa;
  color: #333;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

#app {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.navbar {
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.brand-name {
  font-weight: bold;
  font-size: 1.5rem;
}

.btn-primary {
  background-color: var(--primary-color);
  border-color: var(--primary-color);
}

.btn-primary:hover {
  background-color: var(--secondary-color);
  border-color: var(--secondary-color);
}

.card {
  border-radius: 8px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
  border: none;
  transition: transform 0.2s;
}

.card:hover {
  transform: translateY(-5px);
}

.footer {
  margin-top: auto;
}

.table {
  border-radius: 8px;
  overflow: hidden;
}

.table thead {
  background-color: var(--light-green);
}

.table-hover tbody tr:hover {
  background-color: rgba(209, 231, 221, 0.3);
}

.form-control:focus {
  border-color: var(--accent-color);
  box-shadow: 0 0 0 0.25rem rgba(117, 183, 152, 0.25);
}
</style>
