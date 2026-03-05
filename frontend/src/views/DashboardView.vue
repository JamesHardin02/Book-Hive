<script setup lang="ts">
import { onMounted, ref } from 'vue'
import PageHeader from '@/components/PageHeader.vue'
import { apiFetch, ApiError } from '@/lib/api'

type Location = { aisle: string; shelf: string }

type LowStockItem = {
  book_id: number
  title: string
  isbn: string
  on_hand: number
  threshold: number
  location: Location | null
}

type LowStockResponse = {
  default_threshold: number
  low_stock: LowStockItem[]
  stockout: LowStockItem[]
}

const loading = ref(true)
const error = ref<string | null>(null)
const data = ref<LowStockResponse | null>(null)

onMounted(async () => {
  loading.value = true
  error.value = null

  try {
    data.value = await apiFetch<LowStockResponse>('/dashboard/low-stock')
  } catch (e) {
    if (e instanceof ApiError) {
      error.value = e.message
    } else {
      error.value = String(e)
    }
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <PageHeader page="Dashboard" />

  <main>
    <p v-if="loading">Loading dashboard...</p>
    <p v-else-if="error" style="color: #c00">Error: {{ error }}</p>
    <section v-else-if="data">
      <p style="margin-bottom: 16px">
        Default low stock threshold: <strong>{{ data.default_threshold }}</strong>
      </p>
      <section id="panel-section">
        <article id="StockOutsPanel">
          <h2>Stockout</h2>
          <table v-if="data.stockout.length">
            <thead>
              <tr>
                <th>Title</th>
                <th>ISBN</th>
                <th>On-Hand</th>
                <th>Threshold</th>
                <th>Aisle</th>
                <th>Shelf</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="row in data.stockout" :key="row.book_id">
                <td>{{ row.title }}</td>
                <td>{{ row.isbn }}</td>
                <td>{{ row.on_hand }}</td>
                <td>{{ row.threshold }}</td>
                <td>{{ row.location?.aisle ?? '—' }}</td>
                <td>{{ row.location?.shelf ?? '—' }}</td>
              </tr>
            </tbody>
          </table>
          <p v-else>No stockouts 🎉</p>
        </article>

        <article id="LowStockPanel">
          <h2>Low Stock</h2>
          <table v-if="data.low_stock.length">
            <thead>
              <tr>
                <th>Title</th>
                <th>ISBN</th>
                <th>On-Hand</th>
                <th>Threshold</th>
                <th>Aisle</th>
                <th>Shelf</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="row in data.low_stock" :key="row.book_id">
                <td>{{ row.title }}</td>
                <td>{{ row.isbn }}</td>
                <td>{{ row.on_hand }}</td>
                <td>{{ row.threshold }}</td>
                <td>{{ row.location?.aisle ?? '—' }}</td>
                <td>{{ row.location?.shelf ?? '—' }}</td>
              </tr>
            </tbody>
          </table>
          <p v-else>No low stock items 🎉</p>
        </article>

        <article id="OverduePanel">
          <h2>Overdue Panel</h2>
          <table>
            <thead>
              <tr>
                <th>Title</th>
                <th>Member</th>
                <th>Due Date</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td>Ipsum Lorem</td>
                <td>John Doe</td>
                <td>10/14/2025</td>
                <td>10 days</td>
              </tr>
            </tbody>
          </table>
        </article>
      </section>

      <article id="BusinessIntelChart">
        <h2>Business Intelligence Chart</h2>
        <select>
          <option>Checkouts by Genre (90 days)</option>
          <option>Sales by Month (12 months)</option>
          <option>Top 10 Most Sold Titles</option>
        </select>
        <img src="/src/assets/BI-Chart-Examples.png" alt="BI Chart Examples" />
      </article>
    </section>
  </main>
</template>

<style scoped>
main {
  display: flex;
  flex-wrap: wrap;
  justify-content: space-around;
  padding: 24px;
}

main article {
  margin: 23px;
}

#panel-section {
  display: flex;
  flex-wrap: wrap;
  justify-content: flex-start;
}

#StockOutsPanel {
  margin-bottom: 32px;
}

#BusinessIntelChart {
  width: 100%;
}

h2 {
  color: #c89600;
}

th,
td {
  border: 1px solid #8080805f;
  padding: 3px;
  text-align: center;
}

img {
  width: 100%;
  aspect-ratio: 16 / 9;
  object-fit: cover;
}
</style>
