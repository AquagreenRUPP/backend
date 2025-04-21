<template>
  <div class="register-container">
    <div class="card register-card">
      <div class="card-body">
        <h2 class="text-center mb-4">
          <span class="brand-name">Aqua<span class="text-success">Green</span></span>
        </h2>
        <div v-if="error" class="alert alert-danger">{{ error }}</div>
        <form @submit.prevent="register">
          <!-- Optional fields -->
          <div class="form-group mb-3">
            <input
              type="email"
              class="form-control"
              v-model="email"
              placeholder="Email"
            />
          </div>
          <div class="form-group mb-3">
            <input
              type="text"
              class="form-control"
              v-model="phone"
              placeholder="Phone"
            />
          </div>
          <!-- Required fields -->
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
          <div class="form-group mb-3">
            <input
              type="password"
              class="form-control"
              v-model="confirmPassword"
              placeholder="Confirm Password"
              required
            />
          </div>
          <button
            type="submit"
            class="btn btn-success w-100 mt-3"
            :disabled="loading"
          >
            <span v-if="loading" class="spinner-border spinner-border-sm mr-2"></span>
            Sign up
          </button>
        </form>
        <div class="mt-3 text-center">
          <p>Already have an account? <router-link to="/login" class="text-success">Log In</router-link></p>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { mapActions } from 'vuex';

export default {
  name: 'RegisterView',
  data() {
    return {
      email: '',
      phone: '',
      username: '',
      password: '',
      confirmPassword: '',
      loading: false,
      error: null
    };
  },
  methods: {
    ...mapActions(['registerUser']),
    async register() {
      this.loading = true;
      this.error = null;
      
      if (this.password !== this.confirmPassword) {
        this.error = 'Passwords do not match';
        this.loading = false;
        return;
      }
      
      // Create a registration payload with only required fields
      const registrationData = {
        username: this.username,
        password: this.password
      };
      
      // Add optional fields only if they have values
      if (this.email) registrationData.email = this.email;
      if (this.phone) registrationData.phone = this.phone;
      
      try {
        await this.registerUser(registrationData);
        this.$router.push('/');
      } catch (error) {
        console.error('Registration error:', error);
        if (error.response && error.response.data) {
          // Handle different types of error responses
          const errorData = error.response.data;
          if (typeof errorData === 'string') {
            this.error = errorData;
          } else if (typeof errorData === 'object') {
            // Format field-specific errors
            const errorMessages = [];
            for (const field in errorData) {
              const messages = Array.isArray(errorData[field]) ? errorData[field].join(', ') : errorData[field];
              errorMessages.push(`${field}: ${messages}`);
            }
            this.error = errorMessages.join('\n');
          } else {
            this.error = 'Registration failed. Please try again.';
          }
        } else {
          this.error = 'Registration failed. Please try again.';
        }
      } finally {
        this.loading = false;
      }
    }
  }
};
</script>

<style scoped>
.register-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background-color: #f8f9fa;
}

.register-card {
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
