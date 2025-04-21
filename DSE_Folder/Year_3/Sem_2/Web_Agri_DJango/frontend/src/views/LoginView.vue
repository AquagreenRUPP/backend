<template>
  <div class="login-container">
    <div class="card login-card">
      <div class="card-body">
        <h2 class="text-center mb-4">
          <span class="brand-name">Aqua<span class="text-success">Green</span></span>
        </h2>
        <div v-if="error" class="alert alert-danger">{{ error }}</div>
        <form @submit.prevent="login">
          <div class="form-group mb-3">
            <input
              type="text"
              class="form-control"
              v-model="username"
              placeholder="Username"
              required
            />
          </div>
          <div class="form-group mb-3">
            <input
              type="password"
              class="form-control"
              v-model="password"
              placeholder="Password"
              required
            />
          </div>
          <button
            type="submit"
            class="btn btn-success w-100 mt-3"
            :disabled="loading"
          >
            <span v-if="loading" class="spinner-border spinner-border-sm mr-2"></span>
            Login
          </button>
        </form>
        <div class="mt-3 text-center">
          <p>Don't have an account? <router-link to="/register" class="text-success">Sign up</router-link></p>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { mapActions } from 'vuex';

export default {
  name: 'LoginView',
  data() {
    return {
      username: '',
      password: '',
      loading: false,
      error: null
    };
  },
  methods: {
    ...mapActions(['loginUser']),
    async login() {
      this.loading = true;
      this.error = null;
      
      try {
        await this.loginUser({
          username: this.username,
          password: this.password
        });
        this.$router.push('/');
      } catch (error) {
        this.error = error.response?.data?.detail || 'Login failed. Please check your credentials.';
      } finally {
        this.loading = false;
      }
    }
  }
};
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background-color: #f8f9fa;
}

.login-card {
  width: 100%;
  max-width: 400px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  border: none;
  border-radius: 10px;
}

.brand-name {
  font-size: 2rem;
  font-weight: bold;
}
</style>
