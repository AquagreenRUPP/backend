<template>
  <div class="chart-section">
    <div class="chart-header d-flex justify-content-between align-items-center mb-3">
      <h5>{{ title }}</h5>
      <div class="btn-group" v-if="showControls">
        <button 
          v-for="type in availableChartTypes" 
          :key="type.value"
          class="btn btn-sm" 
          :class="chartType === type.value ? 'btn-success' : 'btn-outline-success'"
          @click="setChartType(type.value)"
        >
          <i :class="type.icon" class="me-1"></i> {{ type.label }}
        </button>
      </div>
    </div>
    
    <div class="chart-wrapper">
      <line-chart 
        v-if="chartType === 'line'" 
        :chart-data="chartData" 
        :options="chartOptions"
      />
      <bar-chart 
        v-else-if="chartType === 'bar'" 
        :chart-data="chartData" 
        :options="chartOptions"
      />
      <pie-chart 
        v-else-if="chartType === 'pie'" 
        :chart-data="chartData" 
        :options="chartOptions"
      />
    </div>
    
    <div class="chart-description text-muted small mt-2" v-if="description">
      {{ description }}
    </div>
  </div>
</template>

<script>
import LineChart from './LineChart.vue';
import BarChart from './BarChart.vue';
import PieChart from './PieChart.vue';

export default {
  name: 'ChartContainer',
  components: {
    LineChart,
    BarChart,
    PieChart
  },
  props: {
    title: {
      type: String,
      required: true
    },
    chartData: {
      type: Object,
      required: true
    },
    options: {
      type: Object,
      default: () => ({})
    },
    description: {
      type: String,
      default: ''
    },
    initialChartType: {
      type: String,
      default: 'line'
    },
    showControls: {
      type: Boolean,
      default: true
    }
  },
  data() {
    return {
      chartType: this.initialChartType,
      availableChartTypes: [
        { value: 'line', label: 'Line', icon: 'bi bi-graph-up' },
        { value: 'bar', label: 'Bar', icon: 'bi bi-bar-chart' },
        { value: 'pie', label: 'Pie', icon: 'bi bi-pie-chart' }
      ]
    };
  },
  computed: {
    chartOptions() {
      return {
        plugins: {
          legend: {
            position: 'top',
          },
          tooltip: {
            mode: 'index',
            intersect: false
          }
        },
        ...this.options
      };
    }
  },
  methods: {
    setChartType(type) {
      this.chartType = type;
    }
  }
};
</script>

<style scoped>
.chart-section {
  background-color: #fff;
  border-radius: 8px;
  padding: 1rem;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  margin-bottom: 1.5rem;
}

.chart-wrapper {
  position: relative;
  width: 100%;
}
</style>
