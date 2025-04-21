<template>
  <div class="file-detail">
    <div v-if="loading" class="text-center my-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
      <p class="mt-2">Loading data...</p>
    </div>

    <div v-else-if="error" class="alert alert-danger">
      {{ error }}
    </div>

    <div v-else-if="!currentFile" class="alert alert-warning">
      File not found. <router-link to="/files">Return to files list</router-link>.
    </div>

    <div v-else>
      <div class="d-flex justify-content-between align-items-center mb-4">
        <h1>{{ currentFile.title }}</h1>
        <router-link to="/files" class="btn btn-outline-secondary">
          Back to Files
        </router-link>
      </div>

      <div class="card mb-4">
        <div class="card-header bg-light">
          <h5 class="card-title mb-0">File Information</h5>
        </div>
        <div class="card-body">
          <div class="row">
            <div class="col-md-6">
              <p><strong>Upload Date:</strong> {{ formatDate(currentFile.uploaded_at) }}</p>
              <p><strong>Status:</strong> 
                <span 
                  :class="currentFile.processed ? 'badge bg-success' : 'badge bg-warning text-dark'"
                >
                  {{ currentFile.processed ? 'Processed' : 'Pending' }}
                </span>
              </p>
            </div>
            <div class="col-md-6">
              <p><strong>File ID:</strong> {{ currentFile.id }}</p>
              <p v-if="!currentFile.processed">
                <button 
                  class="btn btn-sm btn-primary"
                  @click="processFile(currentFile.id)"
                  :disabled="processingFile"
                >
                  <span v-if="processingFile" class="spinner-border spinner-border-sm me-1" role="status" aria-hidden="true"></span>
                  Process File
                </button>
              </p>
            </div>
          </div>
        </div>
      </div>

      <div class="card">
        <div class="card-header bg-light d-flex justify-content-between align-items-center">
          <h5 class="card-title mb-0">Processed Data</h5>
          <div class="btn-group" role="group">
            <button class="btn btn-sm btn-outline-primary" @click="refreshData">
              <i class="bi bi-arrow-clockwise me-1"></i> Refresh
            </button>
            <button class="btn btn-sm btn-outline-success" @click="exportCSV">
              <i class="bi bi-download me-1"></i> Export CSV
            </button>
          </div>
        </div>
        <div class="card-body">
          <div v-if="!currentFile.processed && !processedData" class="alert alert-warning">
            This file has not been processed yet. Click "Process File" to extract the data.
          </div>
          
          <div v-else-if="!processedData || processedData.length === 0" class="alert alert-info">
            No processed data available for this file.
          </div>
          
          <div v-else>
            <!-- Data Table -->
            <div class="table-responsive">
              <table class="table table-striped table-hover">
                <thead>
                  <tr>
                    <th v-for="(_, key) in processedData[0]" :key="key">{{ formatColumnName(key) }}</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(row, index) in processedData" :key="index">
                    <td v-for="(value, key) in row" :key="key">{{ value }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
            
            <!-- Power BI Iframe Preview Placeholder -->
            <div class="mt-4">
              <h5>Data Visualization</h5>
              <div class="alert alert-info">
                Power BI integration will be available in a future update.
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { mapState, mapActions } from 'vuex'

export default {
  name: 'FileDetailView',
  props: {
    id: {
      type: [String, Number],
      required: true
    }
  },
  data() {
    return {
      processingFile: false
    }
  },
  computed: {
    ...mapState(['currentFile', 'processedData', 'loading', 'error'])
  },
  mounted() {
    this.fetchFileData()
  },
  methods: {
    ...mapActions(['fetchFile', 'fetchProcessedData', 'processFile']),
    fetchFileData() {
      this.$store.dispatch('fetchFile', this.id)
      this.$store.dispatch('fetchProcessedData', this.id)
    },
    refreshData() {
      this.fetchFileData()
    },
    async processFile(fileId) {
      this.processingFile = true
      
      try {
        await this.$store.dispatch('processFile', fileId)
        this.$toast.success('File processed successfully')
        this.fetchFileData()
      } catch (error) {
        this.$toast.error('Failed to process file')
        console.error('Error processing file:', error)
      } finally {
        this.processingFile = false
      }
    },
    formatDate(dateString) {
      if (!dateString) return ''
      
      const date = new Date(dateString)
      return new Intl.DateTimeFormat('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      }).format(date)
    },
    formatColumnName(key) {
      if (!key) return ''
      
      // Convert snake_case or camelCase to Title Case
      return key
        .replace(/_/g, ' ')
        .replace(/([A-Z])/g, ' $1')
        .replace(/^./, str => str.toUpperCase())
        .trim()
    },
    exportCSV() {
      if (!this.processedData || this.processedData.length === 0) {
        this.$toast.error('No data to export')
        return
      }
      
      // Get all unique keys from all objects
      const allKeys = this.processedData.reduce((keys, item) => {
        Object.keys(item).forEach(key => {
          if (!keys.includes(key)) {
            keys.push(key)
          }
        })
        return keys
      }, [])
      
      // Create CSV header row
      let csv = allKeys.map(key => `"${this.formatColumnName(key)}"`).join(',') + '\n'
      
      // Add data rows
      this.processedData.forEach(item => {
        const row = allKeys.map(key => {
          const value = item[key] !== undefined ? item[key] : ''
          return `"${value}"`
        }).join(',')
        csv += row + '\n'
      })
      
      // Create download link
      const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' })
      const url = URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.setAttribute('href', url)
      link.setAttribute('download', `${this.currentFile?.title || 'data'}_export.csv`)
      link.style.visibility = 'hidden'
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
    }
  }
}
</script>
