<script setup lang="ts">
import { RouterLink } from 'vue-router'
</script>

<template>
  <nav>
    <RouterLink to="/dashboard">Dashboard</RouterLink>
    <RouterLink to="/inventory">Inventory</RouterLink>
    <RouterLink to="/inventory/add">Add Book</RouterLink>

    <RouterLink to="/members">Members</RouterLink>
    <RouterLink to="/checkout">Checkout</RouterLink>
    <RouterLink to="/returns">Returns</RouterLink>

    <RouterLink to="/sales">Sales</RouterLink>
    <RouterLink to="/exports">Exports</RouterLink>
    <RouterLink to="/search">Search</RouterLink>

    <RouterLink to="/logout">Logout</RouterLink>
  </nav>
</template>

<style scoped>
nav {
  width: 100%;
  text-align: center;
  margin-top: 2rem;
  margin: auto 0px;
}

nav a {
  display: inline-block;
  padding: 0 1rem;
  border-left: 1px solid var(--color-border);
  padding: 15px 15px;
}

nav a.router-link-exact-active {
  color: var(--color-text);
}

nav a.router-link-exact-active:hover {
  background-color: transparent;
}

nav a:first-of-type {
  border: 0;
}

/* Small laptops and up */
@media (min-width: 768px) {
  nav a {
    padding: 5px 10px;
  }
}
</style>
