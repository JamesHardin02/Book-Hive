<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import type {
  PlotlyModule,
  PlotlyConfig,
  PlotlyDatum,
  PlotlyLayout,
} from 'plotly.js-basic-dist-min'

const props = defineProps<{
  data: PlotlyDatum[]
  layout?: PlotlyLayout
  config?: PlotlyConfig
}>()

const chartEl = ref<HTMLElement | null>(null)
let plotlyLib: PlotlyModule | null = null

const primaryTraceType = computed(() => {
  const first = props.data[0] as Record<string, unknown> | undefined
  return typeof first?.type === 'string' ? first.type : 'scatter'
})

async function ensurePlotly(): Promise<PlotlyModule> {
  if (plotlyLib) return plotlyLib

  const mod = await import('plotly.js-basic-dist-min')
  const loaded: PlotlyModule = mod.default ?? mod
  plotlyLib = loaded
  return loaded
}

async function renderChart(): Promise<void> {
  if (!chartEl.value) return

  const Plotly = await ensurePlotly()

  Plotly.purge(chartEl.value)
  await Plotly.newPlot(chartEl.value, props.data, props.layout ?? {}, props.config ?? {})
}

function handleResize(): void {
  if (!chartEl.value || !plotlyLib?.Plots?.resize) return
  plotlyLib.Plots.resize(chartEl.value)
}

onMounted(async () => {
  await renderChart()
  window.addEventListener('resize', handleResize)
})

watch(
  () => [props.data, props.layout, props.config, primaryTraceType.value],
  async () => {
    await renderChart()
  },
  { deep: true },
)

onBeforeUnmount(() => {
  window.removeEventListener('resize', handleResize)
  if (chartEl.value && plotlyLib) {
    plotlyLib.purge(chartEl.value)
  }
})
</script>

<template>
  <div ref="chartEl" class="plotly-chart"></div>
</template>

<style scoped>
.plotly-chart {
  width: 100%;
  min-height: 420px;
}
</style>
