<script setup lang="ts">
import PageHeader from '@/components/PageHeader.vue'
</script>

<template>
  <PageHeader page="Search" />
  <main>
    <table>
      <thead>
        <tr>
          <th><input type="text" placeholder="Title" /></th>
          <th><input type="text" placeholder="Author" /></th>
          <th>
            <select>
              <option>Mystery</option>
              <option>Sci-fi</option>
              <option>Memoir</option>
            </select>
          </th>
          <th><input type="number" placeholder="Year-Min" /></th>
          <th><input type="number" placeholder="Year-Max" /></th>
          <th><input type="text" placeholder="ISBN" /></th>
          <th><input type="text" placeholder="Aisle" /></th>
          <th><input type="text" placeholder="Shelf" /></th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td>Lorem Ipsum</td>
          <td>Jane Doe</td>
          <td>Mystery</td>
          <td>1998</td>
          <td>2001</td>
          <td>978-1-4028-9462-6</td>
          <td>B</td>
          <td>2</td>
        </tr>
        <tr>
          <td>Sit At Amor</td>
          <td>John Doe</td>
          <td>Memoir</td>
          <td>2015</td>
          <td>2017</td>
          <td>978-0-553-21311-7</td>
          <td>A</td>
          <td>3</td>
        </tr>
      </tbody>
    </table>
  </main>
</template>

<style scoped></style>
