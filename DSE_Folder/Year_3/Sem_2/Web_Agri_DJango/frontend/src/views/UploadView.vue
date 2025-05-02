<template>
  <div class="upload-view">
    <h1 class="text-success mb-4">Upload Greenhouse Data</h1>
    
    <div class="card border-success mb-4">
      <div class="card-header bg-success text-white">
        <h5 class="card-title mb-0">Upload Excel File</h5>
      </div>
      <div class="card-body">
        <form @submit.prevent="uploadFile">
          <div class="mb-3">
            <label for="title" class="form-label">Title</label>
            <input
              type="text"
              class="form-control"
              id="title"
              v-model="title"
              placeholder="Enter a descriptive title for your data"
              required
            />
            <div class="form-text">Give your file a meaningful name related to your greenhouse data.</div>
          </div>
          
          <div class="mb-3">
            <label for="file" class="form-label">Excel File</label>
            <input
              type="file"
              class="form-control"
              id="file"
              @change="handleFileChange"
              accept=".xlsx,.xls"
              required
            />
            <div class="form-text">Accepted formats: .xlsx, .xls (Excel files only)</div>
          </div>
          
          <div v-if="fileError" class="alert alert-danger">
            {{ fileError }}
          </div>
          <div v-if="previewError" class="alert alert-danger">
            {{ previewError }}
          </div>
          <div class="d-flex gap-2 mb-3">
            <button type="button" class="btn btn-info" :disabled="!file || previewLoading" @click="previewFile">
              <span v-if="previewLoading" class="spinner-border spinner-border-sm me-2"></span>
              Preview Data
            </button>
            <button type="submit" class="btn btn-success" :disabled="loading || !file || !previewData.length">
              <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
              Confirm Upload
            </button>
          </div>
          <div v-if="previewData.length">
            <h5>Data Preview (first 5 rows)</h5>
            <table class="table table-bordered">
              <thead>
                <tr>
                  <th v-for="header in Object.keys(previewData[0])" :key="header">{{ header }}</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(row, idx) in previewData" :key="idx">
                  <td v-for="header in Object.keys(row)" :key="header">{{ row[header] }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </form>
      </div>
    </div>
    
    <div class="card border-success">
      <div class="card-header bg-success text-white">
        <h5 class="card-title mb-0">Upload Guidelines</h5>
      </div>
      <div class="card-body">
        <h6 class="card-subtitle mb-3 text-success">How to prepare your greenhouse data files:</h6>
        <ul class="list-group list-group-flush mb-3">
          <li class="list-group-item bg-light">
            <i class="bi bi-check-circle-fill text-success me-2"></i>
            Ensure your Excel file contains greenhouse sensor data in a structured format
          </li>
          <li class="list-group-item">
            <i class="bi bi-check-circle-fill text-success me-2"></i>
            Our system automatically detects and processes all columns in your Excel file
          </li>
          <li class="list-group-item bg-light">
            <i class="bi bi-check-circle-fill text-success me-2"></i>
            Include headers in your Excel file for better data identification
          </li>
          <li class="list-group-item">
            <i class="bi bi-check-circle-fill text-success me-2"></i>
            Maximum file size: 10MB
          </li>
        </ul>
        <div class="alert alert-success">
          <i class="bi bi-info-circle-fill me-2"></i>
          After uploading, you can view and analyze your data in the <router-link to="/files" class="alert-link">Files section</router-link>.
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { mapState, mapActions } from 'vuex';
import * as XLSX from 'xlsx';

export default {
  name: 'UploadView',
  data() {
    return {
      title: '',
      file: null,
      fileError: null,
      previewData: [],
      previewLoading: false,
      previewError: null
    };
  },
  computed: {
    ...mapState(['loading', 'error'])
  },
  methods: {
    ...mapActions(['uploadFile']),
    handleFileChange(event) {
      const selectedFile = event.target.files[0];
      this.fileError = null;
      
      if (!selectedFile) {
        this.file = null;
        return;
      }
      
      // Check file type
      const validTypes = ['application/vnd.ms-excel', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'];
      if (!validTypes.includes(selectedFile.type)) {
        this.fileError = 'Invalid file type. Please upload an Excel file (.xlsx or .xls)';
        this.file = null;
        return;
      }
      
      // Check file size (10MB max)
      const maxSize = 10 * 1024 * 1024; // 10MB in bytes
      if (selectedFile.size > maxSize) {
        this.fileError = 'File is too large. Maximum size is 10MB';
        this.file = null;
        return;
      }
      
      this.file = selectedFile;
    },
    async previewFile() {
      this.previewError = null;
      this.previewLoading = true;
      try {
        this.previewData = await this.parseExcel(this.file);
      } catch (err) {
        this.previewError = 'Failed to parse file';
      } finally {
        this.previewLoading = false;
      }
    },
    parseExcel(file) {
      return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = e => {
          const data = new Uint8Array(e.target.result);
          const workbook = XLSX.read(data, { type: 'array' });
          const firstSheet = workbook.SheetNames[0];
          const worksheet = workbook.Sheets[firstSheet];
          const json = XLSX.utils.sheet_to_json(worksheet, { header: 1 });
          const headers = json[0] || [];
          const rows = json.slice(1, 6);
          const result = rows.map(row => {
            const obj = {};
            headers.forEach((header, idx) => {
              obj[header] = row[idx];
            });
            return obj;
          });
          resolve(result);
        };
        reader.onerror = err => reject(err);
        reader.readAsArrayBuffer(file);
      });
    },
    async uploadFile() {
      if (!this.file) {
        this.fileError = 'Please select a file to upload';
        return;
      }
      
      try {
        console.log('Starting file upload...');
        const response = await this.$store.dispatch('uploadFile', {
          title: this.title,
          file: this.file
        });
        
        console.log('Upload successful:', response);
        
        // Reset form
        this.title = '';
        this.file = null;
        document.getElementById('file').value = '';
        
        // Show success message
        this.$toast.success('File uploaded successfully');
        
        // Wait a moment to ensure files are fetched before navigation
        setTimeout(() => {
          // Redirect to files page
          console.log('Redirecting to files page...');
          this.$router.push('/files');
        }, 500);
      } catch (error) {
        console.error('Upload error in component:', error);
        this.fileError = error.message || 'Failed to upload file';
      }
    }
  }
};
</script>

<style scoped>
.card {
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
  border-radius: 8px;
}

.list-group-item {
  border-left: none;
  border-right: none;
}

.list-group-item:first-child {
  border-top: none;
}

.list-group-item:last-child {
  border-bottom: none;
}
</style>
