<template>
  <div class="home">
    <div class="jumbotron bg-light p-5 rounded mb-4">
      <h1 class="display-4 text-success">Welcome to AquaGreen</h1>
      <p class="lead">Greenhouse Management & Data Processing System</p>
      <hr class="my-4">
      <p>Upload your Excel files, process data, and visualize greenhouse metrics in one place.</p>
      <router-link to="/upload" class="btn btn-success btn-lg">Upload Excel File</router-link>
    </div>

    <div class="row mt-5">
      <div class="col-md-4 mb-4">
        <div class="card h-100 border-success">
          <div class="card-header bg-success text-white">
            <h5 class="card-title mb-0">Upload Data</h5>
          </div>
          <div class="card-body">
            <p class="card-text">Upload your greenhouse Excel data files for processing and analysis.</p>
            <router-link to="/upload" class="btn btn-outline-success">Upload Files</router-link>
          </div>
        </div>
      </div>
      
      <div class="col-md-4 mb-4">
        <div class="card h-100 border-success">
          <div class="card-header bg-success text-white">
            <h5 class="card-title mb-0">View Files</h5>
          </div>
          <div class="card-body">
            <p class="card-text">View and manage your uploaded greenhouse data files.</p>
            <router-link to="/files" class="btn btn-outline-success">View Files</router-link>
          </div>
        </div>
      </div>
      
      <div class="col-md-4 mb-4">
        <div class="card h-100 border-success">
          <div class="card-header bg-success text-white">
            <h5 class="card-title mb-0">Data Visualization</h5>
          </div>
          <div class="card-body">
            <p class="card-text">Visualize your greenhouse metrics and analyze trends.</p>
            <router-link to="/files" class="btn btn-outline-success">Analyze Data</router-link>
          </div>
        </div>
      </div>
    </div>

    <div class="row mt-4">
      <div class="col-12">
        <div class="card border-success">
          <div class="card-header bg-success text-white">
            <h5 class="card-title mb-0">About AquaGreen</h5>
          </div>
          <div class="card-body">
            <p>AquaGreen is a comprehensive greenhouse management system that helps you:</p>
            <ul>
              <li>Upload and process Excel data files from your greenhouse sensors</li>
              <li>Automatically extract and organize data without predefined column structures</li>
              <li>Visualize key metrics and trends in your greenhouse environment</li>
              <li>Make data-driven decisions to optimize your greenhouse operations</li>
            </ul>
            <p>Our system uses advanced data processing techniques to handle various Excel formats and provide meaningful insights for your greenhouse management needs.</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'HomeView'
}
</script>

<style scoped>
.jumbotron {
  background-color: #d1e7dd !important;
  border-left: 5px solid #198754;
}

.card {
  transition: transform 0.3s;
}

.card:hover {
  transform: translateY(-5px);
}
</style>
