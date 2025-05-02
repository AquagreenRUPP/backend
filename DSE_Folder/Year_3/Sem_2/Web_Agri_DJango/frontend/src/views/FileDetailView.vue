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
            <!-- Excel Viewer -->
            <excel-viewer 
              :data="processedData" 
              @export-csv="exportCSV"
            />
            
            <!-- Data Visualization Section -->
            <div class="mt-4">
              <h5 class="mb-3">Data Visualization</h5>
              
              <div class="row">
                <!-- Soil Metrics Charts -->
                <div class="col-md-6 mb-4">
                  <chart-container
                    v-if="soilMetricsData.datasets.length > 0"
                    title="Soil Metrics Comparison"
                    :chart-data="soilMetricsData"
                    :options="barChartOptions"
                    description="Comparison of soil pH, moisture, temperature and EC"
                    initial-chart-type="bar"
                  />
                </div>
                
                <!-- Plant Health Chart -->
                <div class="col-md-6 mb-4">
                  <chart-container
                    v-if="plantHealthData.datasets.length > 0"
                    title="Plant Health Metrics"
                    :chart-data="plantHealthData"
                    :options="lineChartOptions"
                    description="Death plants count over time"
                  />
                </div>
                
                <!-- Financial Overview -->
                <div class="col-md-6 mb-4">
                  <chart-container
                    v-if="financialData.labels.length > 0"
                    title="Financial Overview"
                    :chart-data="financialData"
                    :options="pieChartOptions"
                    description="Income vs Expenses breakdown"
                    initial-chart-type="pie"
                  />
                </div>
                
                <!-- Soil pH Distribution -->
                <div class="col-md-6 mb-4">
                  <chart-container
                    v-if="soilPhDistributionData.labels.length > 0"
                    title="Soil pH Distribution"
                    :chart-data="soilPhDistributionData"
                    :options="pieChartOptions"
                    description="Distribution of soil pH levels"
                    initial-chart-type="pie"
                  />
                </div>
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
import ChartContainer from '@/components/charts/ChartContainer.vue'
import ExcelViewer from '@/components/ExcelViewer.vue'

export default {
  name: 'FileDetailView',
  components: {
    ChartContainer,
    ExcelViewer
  },
  // Remove props and use route params directly
  data() {
    return {
      processingFile: false,
      barChartOptions: {
        scales: {
          y: {
            beginAtZero: true,
            title: {
              display: true,
              text: 'Value'
            }
          }
        },
        plugins: {
          legend: {
            position: 'top'
          }
        }
      },
      lineChartOptions: {
        scales: {
          y: {
            beginAtZero: true,
            title: {
              display: true,
              text: 'Count'
            }
          }
        }
      },
      pieChartOptions: {
        plugins: {
          legend: {
            position: 'right'
          }
        }
      },
      // Sample financial data - this would typically come from your backend
      financialSummary: {
        income: 12500,
        expenses: 7800,
        categories: {
          income: {
            'Crop Sales': 9500,
            'Equipment Rental': 2000,
            'Subsidies': 1000
          },
          expenses: {
            'Seeds': 1200,
            'Fertilizer': 2500,
            'Labor': 3000,
            'Equipment': 1100
          }
        }
      }
    }
  },
  computed: {
    ...mapState(['currentFile', 'processedData', 'loading', 'error']),
    
    // Soil metrics chart data
    soilMetricsData() {
      if (!this.processedData || !this.processedData.length) return { labels: [], datasets: [] };
      
      // Get record numbers for labels
      const labels = this.processedData.map(item => `Record ${item.record_no || ''}`).slice(0, 10);
      
      // Extract soil metrics data
      const soilPhData = this.processedData.map(item => parseFloat(item.soil_ph || 0)).slice(0, 10);
      const soilMoistureData = this.processedData.map(item => parseFloat(item.soil_moisture || 0)).slice(0, 10);
      const soilTempData = this.processedData.map(item => parseFloat(item.soil_temp || 0)).slice(0, 10);
      const soilEcData = this.processedData.map(item => parseFloat(item.soil_ec || 0) * 100).slice(0, 10); // Scale EC for visibility
      
      return {
        labels: labels,
        datasets: [
          {
            label: 'Soil pH',
            data: soilPhData,
            backgroundColor: 'rgba(255, 99, 132, 0.7)',
            borderColor: 'rgb(255, 99, 132)',
            borderWidth: 1
          },
          {
            label: 'Soil Moisture',
            data: soilMoistureData,
            backgroundColor: 'rgba(54, 162, 235, 0.7)',
            borderColor: 'rgb(54, 162, 235)',
            borderWidth: 1
          },
          {
            label: 'Soil Temp',
            data: soilTempData,
            backgroundColor: 'rgba(255, 206, 86, 0.7)',
            borderColor: 'rgb(255, 206, 86)',
            borderWidth: 1
          },
          {
            label: 'Soil EC (x100)',
            data: soilEcData,
            backgroundColor: 'rgba(75, 192, 192, 0.7)',
            borderColor: 'rgb(75, 192, 192)',
            borderWidth: 1
          }
        ]
      };
    },
    
    // Plant health data
    plantHealthData() {
      if (!this.processedData || !this.processedData.length) return { labels: [], datasets: [] };
      
      // Get dates for labels
      const labels = this.processedData.map(item => item.date || '');
      
      // Extract plant health data
      const deathPlantsData = this.processedData.map(item => parseInt(item.death_plants || 0));
      
      return {
        labels: labels,
        datasets: [
          {
            label: 'Death Plants',
            data: deathPlantsData,
            borderColor: 'rgb(255, 99, 132)',
            backgroundColor: 'rgba(255, 99, 132, 0.2)',
            borderWidth: 2,
            tension: 0.2,
            fill: true
          }
        ]
      };
    },
    
    // Financial data for income/expense tracking
    financialData() {
      // This would typically come from your backend
      // Using sample data for now
      return {
        labels: ['Income', 'Expenses'],
        datasets: [
          {
            data: [this.financialSummary.income, this.financialSummary.expenses],
            backgroundColor: [
              'rgba(75, 192, 192, 0.7)',
              'rgba(255, 99, 132, 0.7)'
            ],
            borderColor: [
              'rgb(75, 192, 192)',
              'rgb(255, 99, 132)'
            ],
            borderWidth: 1
          }
        ]
      };
    },
    
    // Soil pH distribution data
    soilPhDistributionData() {
      if (!this.processedData || !this.processedData.length) return { labels: [], datasets: [] };
      
      // Count occurrences of different pH ranges
      const phRanges = {
        'Very Acidic (<5.5)': 0,
        'Acidic (5.5-6.5)': 0,
        'Neutral (6.5-7.5)': 0,
        'Alkaline (>7.5)': 0
      };
      
      this.processedData.forEach(item => {
        const ph = parseFloat(item.soil_ph || 0);
        if (ph < 5.5) {
          phRanges['Very Acidic (<5.5)']++;
        } else if (ph >= 5.5 && ph < 6.5) {
          phRanges['Acidic (5.5-6.5)']++;
        } else if (ph >= 6.5 && ph < 7.5) {
          phRanges['Neutral (6.5-7.5)']++;
        } else if (ph >= 7.5) {
          phRanges['Alkaline (>7.5)']++;
        }
      });
      
      return {
        labels: Object.keys(phRanges),
        datasets: [
          {
            data: Object.values(phRanges),
            backgroundColor: [
              'rgba(255, 99, 132, 0.7)',
              'rgba(255, 206, 86, 0.7)',
              'rgba(75, 192, 192, 0.7)',
              'rgba(153, 102, 255, 0.7)'
            ],
            borderColor: [
              'rgb(255, 99, 132)',
              'rgb(255, 206, 86)',
              'rgb(75, 192, 192)',
              'rgb(153, 102, 255)'
            ],
            borderWidth: 1
          }
        ]
      };
    }
  },
  mounted() {
    this.fetchFileData()
  },
  methods: {
    ...mapActions(['fetchFile', 'fetchProcessedData', 'processFile']),
    fetchFileData() {
      // Get ID from route params
      const fileId = this.$route.params.id;
      
      // Validate ID before making API calls
      if (!fileId || fileId === 'undefined' || fileId === 'null') {
        console.error('Invalid file ID:', fileId);
        this.$toast.error('Invalid file ID');
        this.$router.push('/files');
        return;
      }
      
      console.log('Fetching file data for ID:', fileId);
      this.$store.dispatch('fetchFile', fileId);
      this.$store.dispatch('fetchProcessedData', fileId);
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
