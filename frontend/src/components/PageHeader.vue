<script setup lang="ts">
import SiteNav from './SiteNav.vue'
import BookSearch from './BookSearch.vue'
defineProps({
  page: { type: String, required: true },
  booksearch: { type: Boolean, default: true },
})
</script>

<template>
  <header>
    <SiteNav />
    <div>
      <img
        src="/src/assets/BookHive-logo-no-text.png"
        style="width: 100px; height: 100px"
        alt="Book Hive Logo"
      />
      <h1>Book Hive - {{ page }}</h1>
    </div>
    <BookSearch v-if="booksearch" />
  </header>
</template>

<style scoped>
header {
  line-height: 1.5;
  max-height: 100vh;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  align-content: center;
  justify-content: center;
  border: 3px solid white;
  padding: 10px;
  border-radius: 10px;
}

div {
  display: flex;
  align-items: center;
}

h1 {
  font-size: 1.2rem;
  margin-left: 20px;
  margin-top: 10px;
}

img {
  width: 100%;
  aspect-ratio: 16 / 9;
  object-fit: cover;
}

/* Small tablets and up */
@media (min-width: 425px) {
  h1 {
    font-size: 1.5rem;
    margin-left: 20px;
    margin-top: 10px;
  }
}

/* Small laptops and up */
@media (min-width: 768px) {
  h1 {
    font-size: 2rem;
  }
}
</style>
