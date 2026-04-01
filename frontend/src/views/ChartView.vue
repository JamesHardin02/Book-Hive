<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
// @ts-ignore: plotly.js-dist has no types in this project
import Plotly from 'plotly.js-dist'

type ChartType = 'genre' | 'sales' | 'top10'

const route = useRoute()
const chartType = computed<ChartType>(() => {
  const value = route.params.type
  if (value === 'sales' || value === 'top10') return value
  return 'genre'
})

const chartDiv = ref<HTMLDivElement | null>(null)

const buildChart = () => {
  if (!chartDiv.value) return

  let data: Plotly.Data[] = []
  let layout: Partial<Plotly.Layout> = {}

  if (chartType.value === 'genre') {
    data = [
      {
        type: 'bar',
        x: ['Fiction', 'Non-Fiction', 'Sci-Fi', 'Romance', 'Mystery'],
        y: [120, 80, 60, 40, 30],
        name: 'Checkouts',
      },
    ]
    layout = { title: { text: 'Checkouts by Genre (90 days)' } }
  } else if (chartType.value === 'sales') {
    data = [
      {
        type: 'scatter',
        mode: 'lines+markers',
        x: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
        y: [100, 120, 150, 130, 160, 180, 200, 190, 170, 140, 110, 90],
        name: 'Sales',
      },
    ]
    layout = { title: { text: 'Sales by Month (12 months)' } }
  } else {
    data = [
      {
        type: 'bar',
        x: ['Book 1', 'Book 2', 'Book 3', 'Book 4', 'Book 5', 'Book 6', 'Book 7', 'Book 8', 'Book 9', 'Book 10'],
        y: [50, 45, 40, 35, 30, 25, 20, 15, 10, 5],
        name: 'Copies Sold',
      },
    ]
    layout = { title: { text: 'Top 10 Most Sold Titles' } }
  }

  Plotly.newPlot(chartDiv.value, data, layout, { responsive: true })
}

onMounted(buildChart)
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