<script setup lang="ts">
const props = defineProps<{
  message?: string
  type?: 'button' | 'submit' | 'reset'
}>()
</script>

<template>
  <button :type="'type' in props ? props.type : 'button'" v-if="message">{{ message }}</button>
  <button v-else>Submit</button>
</template>

<style>
button {
  padding: 0.5rem;
  background-color: #e8c456;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  width: 100%;
}
button:hover {
  background-color: #d4b04a;
}
</style>
