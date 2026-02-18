<script setup lang="ts">
import { RouterLink } from 'vue-router'
import BaseButton from './BaseButton.vue'
</script>

<template>
  <form>
    <input placeholder="Search ISBN or Title" />
    <RouterLink to="/search">
      <BaseButton style="width: 25%" message="Search" type="button" />
    </RouterLink>
  </form>
</template>

<style></style>
