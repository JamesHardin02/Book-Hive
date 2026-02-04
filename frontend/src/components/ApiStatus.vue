<script setup lang="ts">
import { ref, onMounted } from 'vue'

const status = ref<string>('Checking...')
const ok = ref<boolean>(false)

onMounted(async () => {
  try {
    const base = import.meta.env.VITE_API_BASE_URL
    const res = await fetch(`${base}/health`)
    const data = await res.json()
    ok.value = Boolean(data.ok)
    status.value = JSON.stringify(data)
  } catch (e) {
    status.value = String(e)
  }
})
</script>

<template>
  <div style="padding: 12px; border: 5px solid #ccc; border-radius: 8px">
    <strong>Backend health:</strong>
    <span v-if="ok === true"> ✅ OK</span>
    <span v-else-if="ok === false"> ❌ FAIL</span>
    <span v-else> ⌛ ...</span>
    <pre style="margin-top: 8px; white-space: pre-wrap">{{ status }}</pre>
  </div>
</template>
