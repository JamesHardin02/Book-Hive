<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref, watch } from 'vue'

const props = withDefaults(
  defineProps<{
    data?: Record<string, unknown>[]
    layout?: Record<string, unknown>
    config?: Record<string, unknown>
    loading?: boolean
  }>(),
  {
    data: () => [],
    layout: () => ({}),
    config: () => ({}),
    loading: false,
  },
)

const host = ref<HTMLDivElement | null>(null)
let plotlyLib: any = null

async function getPlotly(): Promise<any> {
  if (!plotlyLib) {
    const mod = await import('plotly.js-basic-dist-min')
    plotlyLib = (mod as { default?: unknown }).default ?? mod
  }
  return plotlyLib
}

async function renderPlot(): Promise<void> {
  if (!host.value || props.loading) return

  const Plotly = await getPlotly()
  await Plotly.react(
    host.value,
    props.data,
    {
      autosize: true,
      margin: { l: 48, r: 16, t: 48, b: 56 },
      paper_bgcolor: 'transparent',
      plot_bgcolor: 'transparent',
      font: { color: '#2c3e50' },
      ...props.layout,
    },
    {
      responsive: true,
      displaylogo: false,
      modeBarButtonsToRemove: ['lasso2d', 'select2d'],
      ...props.config,
    },
  )
}

watch(
  () => [props.data, props.layout, props.config, props.loading],
  () => {
    if (!props.loading) {
      void renderPlot()
    }
  },
  { deep: true },
)

onMounted(() => {
  if (!props.loading) {
    void renderPlot()
  }
})

onBeforeUnmount(async () => {
  if (!host.value) return
  const Plotly = await getPlotly()
  Plotly.purge(host.value)
})
</script>

<template>
  <div ref="host" class="plot-host" :aria-busy="loading ? 'true' : 'false'"></div>
</template>

<style scoped>
.plot-host {
  width: 100%;
  min-height: 420px;
}
</style>
