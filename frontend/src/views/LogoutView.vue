<script setup lang="ts">
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const auth = useAuthStore()

onMounted(() => {
  auth.logout()
  router.replace('/')
})
</script>

<template>
  <main style="padding: 24px">
    <p>Logging out...</p>
  </main>
</template>
