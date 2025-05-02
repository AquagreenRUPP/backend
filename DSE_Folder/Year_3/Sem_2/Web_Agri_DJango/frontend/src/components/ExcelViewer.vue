<template>
  <div class="excel-viewer">
    <div class="excel-toolbar mb-2 d-flex justify-content-between align-items-center">
      <div class="btn-group">
        <button class="btn btn-sm btn-outline-secondary" @click="downloadExcel">
          <i class="bi bi-file-earmark-excel me-1"></i> Download Excel
        </button>
        <button class="btn btn-sm btn-outline-success" @click="$emit('export-csv')">
          <i class="bi bi-download me-1"></i> Export CSV
        </button>
      </div>
      
      <!-- Data table type selector -->
      <div class="table-type-selector">
        <span class="me-2">Data Type:</span>
        <select class="form-select form-select-sm" v-model="detectedTableType" style="width: auto; display: inline-block;">
          <option value="environmental">Environmental Data</option>
          <option value="production">Production Data</option>
          <option value="averages">Environmental Averages</option>
          <option value="generic">Generic Data</option>
        </select>
      </div>
    </div>
    
    <div v-if="!data || data.length === 0" class="alert alert-info">
      No data available to display.
    </div>
    
    <div v-if="data && data.length > 0" class="excel-container">
      <div class="excel-header">
        <!-- Column headers (A, B, C, etc.) -->
        <div class="excel-corner-cell"></div>
        <div 
          v-for="(col, colIndex) in columnLetters.slice(0, sortedColumns.length)" 
          :key="'col-' + colIndex" 
          class="excel-header-cell"
        >
          {{ col }}
        </div>
      </div>
      
      <!-- Column names row -->
      <div class="excel-column-names">
        <div class="excel-row-header">#</div>
        <div 
          v-for="(col, colIndex) in sortedColumns" 
          :key="'colname-' + colIndex" 
          class="excel-column-name"
          :title="col"
        >
          {{ formatColumnName(col) }}
        </div>
      </div>
      
      <div class="excel-body">
        <div 
          class="excel-row" 
          v-for="(row, rowIndex) in data" 
          :key="'row-' + rowIndex"
          :class="{ 'excel-row-even': rowIndex % 2 === 0 }"
        >
          <!-- Row numbers (1, 2, 3, etc.) -->
          <div class="excel-row-header">{{ rowIndex + 1 }}</div>
          
          <!-- Data cells -->
          <div 
            v-for="(col, colIndex) in sortedColumns" 
            :key="'cell-' + rowIndex + '-' + colIndex" 
            class="excel-cell"
            :class="{
              // Generic styling
              'numeric-cell': typeof row[col] === 'number',
              'date-cell': col.toLowerCase().includes('date') || col.toLowerCase() === 'time',
              
              // Fix_Column.xlsx styling
              'soil-ph-cell': col.toLowerCase() === 'soil_ph',
              'soil-moisture-cell': col.toLowerCase() === 'soil_moisture',
              'soil-temp-cell': col.toLowerCase() === 'soil_temp',
              'soil-ec-cell': col.toLowerCase() === 'soil_ec',
              
              // Environmental Data styling
              'temperature-cell': col.toLowerCase().includes('temperature'),
              'humidity-cell': col.toLowerCase().includes('humidity'),
              'rain-cell': col.toLowerCase() === 'rain',
              'soil-moisture-env-cell': col.toLowerCase().includes('soil_moisture_'),
              
              // Production Data styling
              'yield-cell': col.toLowerCase() === 'total_yield',
              'financial-cell': ['income', 'expense', 'net_income'].includes(col.toLowerCase()),
              'identifier-cell': col.toLowerCase() === 'nethouse_code' || col.toLowerCase() === 'crop_type',
              
              // Environmental Averages styling
              'average-temp-cell': col.toLowerCase().includes('avg') && col.toLowerCase().includes('temp'),
              'average-humidity-cell': col.toLowerCase().includes('avg') && col.toLowerCase().includes('humidity'),
              'total-rainfall-cell': col.toLowerCase() === 'total_rainfall',
              'average-moisture-cell': col.toLowerCase().includes('soil_moisture_')
            }"
          >
            {{ formatCellValue(row[col], col) }}
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import * as XLSX from 'xlsx';

export default {
  name: 'ExcelViewer',
  props: {
    data: {
      type: Array,
      required: true
    }
  },
  data() {
    return {
      columnLetters: 'ABCDEFGHIJKLMNOPQRSTUVWXYZ',
      detectedTableType: 'generic' // Will be auto-detected based on columns
    }
  },
  computed: {
    columns() {
      if (!this.data || this.data.length === 0) return [];
      
      // Get all unique keys from all objects
      return this.data.reduce((keys, item) => {
        Object.keys(item).forEach(key => {
          if (!keys.includes(key)) {
            keys.push(key);
          }
        });
        return keys;
      }, []);
    },
    rows() {
      if (!this.data || this.data.length === 0) return [];
      
      // Create an array with header row + data rows
      return [null, ...this.data];
    },
    // Auto-detect table type based on columns
    tableType() {
      if (!this.data || this.data.length === 0) return 'generic';
      
      const columnNames = this.columns.map(col => col.toLowerCase());
      
      // Check for Environmental Data Table
      if (columnNames.includes('time') && 
          (columnNames.includes('temperature_2m') || columnNames.includes('soil_temperature_0cm'))) {
        return 'environmental';
      }
      
      // Check for Production Data Table
      if (columnNames.includes('nethouse_code') && 
          (columnNames.includes('crop_type') || columnNames.includes('total_yield'))) {
        return 'production';
      }
      
      // Check for Environmental Averages Table
      if (columnNames.includes('growing_period') && 
          (columnNames.includes('avg_air_temp_2m') || columnNames.includes('avg_soil_temp_0cm'))) {
        return 'averages';
      }
      
      // Check for Fix_Column.xlsx format
      if (columnNames.includes('record_no') && 
          (columnNames.includes('soil_ph') || columnNames.includes('soil_ec'))) {
        return 'fix_column';
      }
      
      return 'generic';
    },
    
    // Sort columns based on the detected table type
    sortedColumns() {
      // Use the user-selected table type or auto-detected type
      const tableType = this.detectedTableType || this.tableType;
      
      // Define column orders for each table type
      const columnOrders = {
        environmental: [
          'time', 'temperature_2m', 'relative_humidity_2m', 'rain', 'weather_code',
          'soil_temperature_0cm', 'soil_temperature_6cm', 'soil_temperature_18cm', 'soil_temperature_54cm',
          'soil_moisture_0_to_1cm', 'soil_moisture_1_to_3cm', 'soil_moisture_3_to_9cm', 
          'soil_moisture_9_to_27cm', 'soil_moisture_27_to_81cm'
        ],
        production: [
          'nethouse_code', 'crop_type', 'germination_date', 'transplantation_date', 'harvest_date',
          'total_yield', 'income', 'expense', 'net_income', 'number_of_plant'
        ],
        averages: [
          'nethouse_code', 'growing_period', 'avg_air_temp_2m', 'avg_relative_humidity', 'total_rainfall',
          'avg_soil_temp_0cm', 'avg_soil_temp_6cm', 'avg_soil_temp_18cm', 'avg_soil_temp_54cm',
          'soil_moisture_0to1cm', 'soil_moisture_1to3cm', 'soil_moisture_3to9cm', 
          'soil_moisture_9to27cm', 'soil_moisture_27to81cm'
        ],
        fix_column: [
          'record_no', 'date', 'death_plants', 'soil_moisture', 'soil_ph', 'soil_temp', 'soil_ec'
        ],
        generic: [
          'id', 'name', 'code', 'date', 'time', 'timestamp', 'temperature', 'humidity', 'moisture'
        ]
      };
      
      // Get the appropriate column order based on table type
      const standardColumns = columnOrders[tableType] || columnOrders.generic;
      
      return [...this.columns].sort((a, b) => {
        // Check if columns are in the standard columns list for this table type
        const aStandardIndex = standardColumns.findIndex(field => 
          a.toLowerCase() === field.toLowerCase() || a.toLowerCase().includes(field.toLowerCase())
        );
        const bStandardIndex = standardColumns.findIndex(field => 
          b.toLowerCase() === field.toLowerCase() || b.toLowerCase().includes(field.toLowerCase())
        );
        
        // If both are standard columns, sort by their position in the standard list
        if (aStandardIndex !== -1 && bStandardIndex !== -1) return aStandardIndex - bStandardIndex;
        
        // If only a is a standard column, it comes first
        if (aStandardIndex !== -1) return -1;
        
        // If only b is a standard column, it comes first
        if (bStandardIndex !== -1) return 1;
        
        // Otherwise sort alphabetically
        return a.localeCompare(b);
      });
    },
    formattedData() {
      if (!this.data || this.data.length === 0) return [];
      
      // Format data for Excel export
      const headers = this.columns;
      
      // Create header row
      const result = [
        headers.map(h => this.formatColumnName(h))
      ];
      
      // Add data rows
      this.data.forEach(item => {
        const row = headers.map(key => item[key] !== undefined ? item[key] : '');
        result.push(row);
      });
      
      return result;
    }
  },
  methods: {
    formatCellValue(value, column) {
      if (value === undefined || value === null) return '';
      
      // Get the current table type
      const tableType = this.detectedTableType || this.tableType;
      const colLower = column ? column.toLowerCase() : '';
      
      // Format dates
      if ((typeof value === 'string' && value.match(/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}/)) ||
          colLower === 'date' ||
          colLower === 'time' ||
          colLower.includes('_date')) {
        return new Date(value).toLocaleDateString();
      }
      
      // Format based on table type and column name
      if (typeof value === 'number') {
        // Environmental Data Table formatting
        if (tableType === 'environmental') {
          // Temperature values (1 decimal place)
          if (colLower.includes('temperature')) {
            return value.toFixed(1) + ' °C';
          }
          // Humidity values (whole number with %)
          else if (colLower.includes('humidity')) {
            return Math.round(value) + ' %';
          }
          // Rainfall (1 decimal place with mm)
          else if (colLower === 'rain') {
            return value.toFixed(1) + ' mm';
          }
          // Soil moisture (3 decimal places with unit)
          else if (colLower.includes('moisture')) {
            return value.toFixed(3) + ' m³/m³';
          }
        }
        
        // Production Data Table formatting
        else if (tableType === 'production') {
          // Yield (whole number with kg)
          if (colLower === 'total_yield') {
            return Math.round(value) + ' kg';
          }
          // Financial values (currency format)
          else if (colLower === 'income' || colLower === 'expense' || colLower === 'net_income') {
            return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(value);
          }
          // Number of plants (whole number)
          else if (colLower === 'number_of_plant') {
            return Math.round(value);
          }
        }
        
        // Environmental Averages Table formatting
        else if (tableType === 'averages') {
          // Temperature averages (1 decimal place)
          if (colLower.includes('temp')) {
            return value.toFixed(1) + ' °C';
          }
          // Humidity average (1 decimal place with %)
          else if (colLower.includes('humidity')) {
            return value.toFixed(1) + ' %';
          }
          // Rainfall (1 decimal place with mm)
          else if (colLower.includes('rainfall')) {
            return value.toFixed(1) + ' mm';
          }
          // Soil moisture (3 decimal places with unit)
          else if (colLower.includes('moisture')) {
            return value.toFixed(3) + ' m³/m³';
          }
        }
        
        // Fix_Column.xlsx formatting
        else if (tableType === 'fix_column') {
          // Special formatting for soil_ph (2 decimal places)
          if (colLower === 'soil_ph') {
            return value.toFixed(2);
          }
          // Special formatting for soil_ec (3 decimal places as it's often very small)
          else if (colLower === 'soil_ec') {
            return value.toFixed(3);
          }
          // Special formatting for soil_moisture and soil_temp (1 decimal place)
          else if (colLower === 'soil_moisture' || colLower === 'soil_temp') {
            return value.toFixed(1);
          }
        }
        
        // Generic number formatting
        // If it's a whole number or has 1-2 decimal places, display as is
        if (Number.isInteger(value) || (value.toString().split('.')[1]?.length <= 2)) {
          return value;
        }
        // Otherwise format to 2 decimal places
        return value.toFixed(2);
      }
      
      return value;
    },
    formatColumnName(key) {
      if (!key) return '';
      
      // Convert snake_case or camelCase to Title Case
      return key
        .replace(/_/g, ' ')
        .replace(/([A-Z])/g, ' $1')
        .replace(/^./, str => str.toUpperCase())
        .trim();
    },
    downloadExcel() {
      if (!this.data || this.data.length === 0) {
        this.$toast?.error('No data to export');
        return;
      }
      
      try {
        // Create a new workbook
        const wb = XLSX.utils.book_new();
        
        // Convert data to worksheet
        const ws = XLSX.utils.aoa_to_sheet(this.formattedData);
        
        // Add worksheet to workbook
        XLSX.utils.book_append_sheet(wb, ws, 'Data');
        
        // Generate Excel file and trigger download
        XLSX.writeFile(wb, 'agricultural_data.xlsx');
      } catch (error) {
        console.error('Error exporting Excel:', error);
        this.$toast?.error('Failed to export Excel file');
      }
    }
  }
}
</script>

<style scoped>
.excel-viewer {
  width: 100%;
  overflow-x: auto;
  border: 1px solid #dee2e6;
  border-radius: 0.25rem;
  background-color: #fff;
}

.excel-toolbar {
  padding: 8px;
  border-bottom: 1px solid #dee2e6;
  background-color: #f8f9fa;
}

.excel-container {
  display: flex;
  flex-direction: column;
}

.excel-header {
  display: flex;
  background-color: #f8f9fa;
  border-bottom: 1px solid #dee2e6;
  position: sticky;
  top: 0;
}

.excel-corner-cell {
  min-width: 40px;
  border-right: 1px solid #dee2e6;
  background-color: #f0f0f0;
}

.excel-header-cell {
  min-width: 120px;
  padding: 8px;
  font-weight: bold;
  text-align: center;
  border-right: 1px solid #dee2e6;
  background-color: #e9ecef;
}

.excel-column-names {
  display: flex;
  background-color: #f8f9fa;
  border-bottom: 2px solid #dee2e6;
  position: sticky;
  top: 0;
  z-index: 2;
}

.excel-column-name {
  min-width: 120px;
  padding: 8px;
  font-weight: bold;
  text-align: center;
  border-right: 1px solid #dee2e6;
  background-color: #f0f0f0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.excel-body {
  display: flex;
  flex-direction: column;
}

.excel-row {
  display: flex;
  border-bottom: 1px solid #dee2e6;
}

.excel-row:hover {
  background-color: rgba(0, 123, 255, 0.1);
}

.excel-row-even {
  background-color: rgba(0, 0, 0, 0.02);
}

.excel-row-header {
  min-width: 40px;
  padding: 8px 4px;
  text-align: center;
  font-weight: bold;
  border-right: 1px solid #dee2e6;
  background-color: #e9ecef;
}

.excel-cell {
  min-width: 120px;
  padding: 8px;
  border-right: 1px solid #dee2e6;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* Special styling for different column types */

/* Generic styling */
.numeric-cell {
  text-align: right;
}

.date-cell {
  font-weight: 500;
}

/* Fix_Column.xlsx styling */
.soil-ph-cell {
  background-color: rgba(255, 230, 230, 0.2);
}

.soil-moisture-cell {
  background-color: rgba(230, 230, 255, 0.2);
}

.soil-temp-cell {
  background-color: rgba(255, 240, 230, 0.2);
}

.soil-ec-cell {
  background-color: rgba(230, 255, 230, 0.2);
}

/* Environmental Data styling */
.temperature-cell {
  background-color: rgba(255, 220, 220, 0.2);
}

.humidity-cell {
  background-color: rgba(220, 220, 255, 0.2);
}

.rain-cell {
  background-color: rgba(220, 240, 255, 0.2);
}

.soil-moisture-env-cell {
  background-color: rgba(230, 255, 230, 0.2);
}

/* Production Data styling */
.yield-cell {
  background-color: rgba(230, 255, 230, 0.2);
  font-weight: 500;
}

.financial-cell {
  background-color: rgba(255, 255, 220, 0.2);
  font-weight: 500;
}

.identifier-cell {
  font-weight: 500;
}

/* Environmental Averages styling */
.average-temp-cell {
  background-color: rgba(255, 235, 220, 0.2);
}

.average-humidity-cell {
  background-color: rgba(220, 235, 255, 0.2);
}

.total-rainfall-cell {
  background-color: rgba(220, 245, 255, 0.2);
}

.average-moisture-cell {
  background-color: rgba(235, 255, 235, 0.2);
}

.excel-header-data {
  font-weight: bold;
  background-color: #f8f9fa;
}
</style>
