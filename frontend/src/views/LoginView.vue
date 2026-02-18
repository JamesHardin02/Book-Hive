<script setup lang="ts">
import { RouterLink } from 'vue-router'
import BaseButton from '@/components/BaseButton.vue'
</script>

<template>
  <main>
    <header>
      <img
        src="/src/assets/BookHive-logo-no-text.png"
        style="width: 100px; height: 100px"
        alt="Book Hive Logo"
      />
      <h1>Book Hive</h1>
    </header>
    <div id="sign-in">
      <h2>Sign In</h2>
      <form>
        <input type="text" placeholder="Username" />
        <input type="password" placeholder="Password" />
        <RouterLink to="/dashboard">
          <BaseButton type="submit" />
        </RouterLink>
        <RouterLink to="/register">
          <BaseButton type="button" message="Create Account" />
        </RouterLink>
      </form>
    </div>
    <footer>
      <h3>Member-only tool. All activity is audited.</h3>
    </footer>
  </main>
</template>

<style scoped>
main {
  margin: 0 auto;
}

main header {
  display: flex;
  align-content: center;
  justify-content: center;
  border: 3px solid white;
  padding: 10px;
  border-radius: 10px;
}

main header h1 {
  font-size: 3rem;
  margin-left: 20px;
  margin-top: 10px;
}

img {
  width: 100%;
  aspect-ratio: 16 / 9;
  object-fit: cover;
}

h2 {
  font-size: 2rem;
  margin-bottom: 1rem;
  display: flex;
  justify-content: center;
}

#sign-in {
  margin: 0 22%;
}

form {
  display: flex;
  flex-direction: column;
}

input {
  padding: 0.5rem;
  margin-bottom: 1rem;
  border: 1px solid #ccc;
  border-radius: 4px;
}

footer {
  margin-top: 2rem;
  text-align: center;
  font-size: 1.2rem;
  color: #555;
}

/* Tablets and up*/
@media (min-width: 770px) {
  #sign-in {
    margin: 0 25%;
  }
}
</style>
