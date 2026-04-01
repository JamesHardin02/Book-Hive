<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import Plotly from 'plotly.js'

const route = useRoute()
const chartType = route.params.type as string
const chartDiv = ref<HTMLDivElement>()

onMounted(() => {
  if (!chartDiv.value) return

  let data: any[] = []
  let layout: any = {}

  if (chartType === 'genre') {
    data = [{
      type: 'bar',
      x: ['Fiction', 'Non-Fiction', 'Sci-Fi', 'Romance', 'Mystery'],
      y: [120, 80, 60, 40, 30],
      name: 'Checkouts'
    }]
    layout = { title: 'Checkouts by Genre (90 days)' }
  } else if (chartType === 'sales') {
    data = [{
      type: 'line',
      x: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
      y: [100, 120, 150, 130, 160, 180, 200, 190, 170, 140, 110, 90],
      name: 'Sales'
    }]
    layout = { title: 'Sales by Month (12 months)' }
  } else if (chartType === 'top10') {
    data = [{
      type: 'bar',
      x: ['Book 1', 'Book 2', 'Book 3', 'Book 4', 'Book 5', 'Book 6', 'Book 7', 'Book 8', 'Book 9', 'Book 10'],
      y: [50, 45, 40, 35, 30, 25, 20, 15, 10, 5],
      name: 'Copies Sold'
    }]
    layout = { title: 'Top 10 Most Sold Titles' }
  }

  Plotly.newPlot(chartDiv.value, data, layout)
})
</script>

<template>
  <div>
    <h1>Interactive Chart: {{ chartType }}</h1>
    <div ref="chartDiv" style="width: 100%; height: 600px;"></div>
    <router-link to="/dashboard">Back to Dashboard</router-link>
  </div>
</template>

<style scoped>
/* Add any styles if needed */
</style>