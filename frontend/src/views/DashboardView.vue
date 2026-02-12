<script setup lang="ts">
import PageHeader from '@/components/PageHeader.vue'
</script>

<template>
  <PageHeader page="Dashboard" />

  <main>
    <article id="LowStockPanel">
      <h2>Low Stock Panel</h2>
      <table>
        <thead>
          <tr>
            <th>Title</th>
            <th>On-Hand</th>
            <th>Min</th>
            <th>Aisle</th>
            <th>Shelf</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td>Lorem Ipsum</td>
            <td>2</td>
            <td>3</td>
            <td>B</td>
            <td>2</td>
          </tr>
          <tr>
            <td>Dolor Sit Amat</td>
            <td>0</td>
            <td>3</td>
            <td>E</td>
            <td>1</td>
          </tr>
        </tbody>
      </table>
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
    <article id="BusinessIntelChart">
      <h2>Business Intelligence Chart</h2>
      <select>
        <option>Checkouts by Genre (90 days)</option>
        <option>Sales by Month (12 months)</option>
        <option>Top 10 Most Sold Titles</option>
      </select>
      <img src="/src/assets/BI-Chart-Examples.png" alt="BI Chart Examples" />
    </article>
  </main>
</template>

<style scoped>
main {
  display: flex;
  flex-wrap: wrap;
  justify-content: space-around;
}

main article {
  margin: 23px;
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
