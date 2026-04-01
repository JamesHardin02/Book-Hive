<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import chartSprite from '@/assets/BI-Chart-Examples.png'
import { apiFetch, ApiError } from '@/lib/api'
import PlotlyChart from '@/components/PlotlyChart.vue'

type ReportFamily = 'sales' | 'circulation' | 'inventory'
type ChartStyle = 'donut' | 'bar' | 'line' | 'area' | 'timeline' | 'waterfall' | 'network'
type BackendReport = 'sales_trends' | 'checkouts_by_genre' | 'top_titles' | 'inventory_health'

type ReportRow = Record<string, string | number | boolean | null>

type SummaryItem = {
  label: string
  value: string
}

type ReportResponse = {
  report: BackendReport
  title: string
  description: string
  available_styles: string[]
  default_style: string
  table_columns: string[]
  detail_columns: string[]
  rows: ReportRow[]
  detail_rows: ReportRow[]
  summary: SummaryItem[]
  empty_message: string
  chart_meta: {
    label_field: string
    primary_value_field: string
    secondary_value_field: string | null
    x_title: string
    y_title: string
  }
}

type Tile = {
  key: ChartStyle
  label: string
  blurb: string
  position: string
  planned?: boolean
}

const reportFamilies: { key: ReportFamily; label: string; blurb: string }[] = [
  {
    key: 'sales',
    label: 'Sales Trends',
    blurb: 'Revenue and unit trends over time.',
  },
  {
    key: 'circulation',
    label: 'Circulation Metrics',
    blurb: 'Genre mix and most-borrowed titles.',
  },
  {
    key: 'inventory',
    label: 'Inventory Health',
    blurb: 'Stock pressure and restocking visibility.',
  },
]

const chartTiles: Tile[] = [
  {
    key: 'donut',
    label: 'Donut chart',
    blurb: 'Category share and composition.',
    position: '0% 0%',
  },
  {
    key: 'bar',
    label: 'Column chart',
    blurb: 'Strong for comparing categories.',
    position: '50% 0%',
  },
  {
    key: 'area',
    label: 'Area & Line charts',
    blurb: 'Best for trend and movement over time.',
    position: '100% 0%',
  },
  {
    key: 'waterfall',
    label: 'Waterfall chart',
    blurb: 'Planned style for future delta analysis.',
    position: '0% 100%',
    planned: true,
  },
  {
    key: 'timeline',
    label: 'Timeline chart',
    blurb: 'Time-bucket views for weekly/monthly reporting.',
    position: '50% 100%',
  },
  {
    key: 'network',
    label: 'Network chart',
    blurb: 'Planned style for future relationship mapping.',
    position: '100% 100%',
    planned: true,
  },
]

const selectedFamily = ref<ReportFamily>('sales')
const selectedStyle = ref<ChartStyle>('line')
const days = ref(365)
const salesBucket = ref<'month' | 'week'>('month')
const salesMetric = ref<'revenue' | 'quantity'>('revenue')
const circulationDataset = ref<'checkouts_by_genre' | 'top_titles'>('checkouts_by_genre')
const topLimit = ref(10)
const inventoryScope = ref<'all' | 'attention_only'>('all')

const report = ref<ReportResponse | null>(null)
const loading = ref(false)
const error = ref<string | null>(null)
const exportMessage = ref<string | null>(null)
const exporting = ref(false)

const supportedStyles = computed(() => new Set(report.value?.available_styles ?? []))
const currentRows = computed(() => report.value?.rows ?? [])
const currentDetailRows = computed(() => report.value?.detail_rows ?? [])
const currentTableColumns = computed(() => {
  if (currentDetailRows.value.length > 0 && report.value?.detail_columns.length) {
    return report.value.detail_columns
  }
  return report.value?.table_columns ?? []
})
const currentTableRows = computed(() => {
  if (currentDetailRows.value.length > 0) {
    return currentDetailRows.value
  }
  return currentRows.value
})
const hasChartData = computed(
  () => currentRows.value.length > 0 || currentDetailRows.value.length > 0,
)

function tilePreviewStyle(tile: Tile): Record<string, string> {
  return {
    backgroundImage: `linear-gradient(rgba(255,255,255,.18), rgba(255,255,255,.18)), url(${chartSprite})`,
    backgroundPosition: tile.position,
    backgroundSize: '300% 200%',
  }
}

function getApiBase(): string {
  return import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
}

function styleDisabled(tile: Tile): boolean {
  if (tile.planned) return true
  return !supportedStyles.value.has(tile.key)
}

function selectStyle(tile: Tile): void {
  if (styleDisabled(tile)) return
  selectedStyle.value = tile.key
}

function familyIsActive(key: ReportFamily): boolean {
  return selectedFamily.value === key
}

function prettyStatus(value: string): string {
  return value.replaceAll('_', ' ').replace(/\b\w/g, (char) => char.toUpperCase())
}

function displayValue(column: string, value: unknown): string {
  if (value === null || value === undefined) return '—'
  if (column === 'revenue' || column === 'unit_price' || column === 'line_total') {
    return `$${Number(value).toFixed(2)}`
  }
  if (column === 'status' && typeof value === 'string') {
    return prettyStatus(value)
  }
  return String(value)
}

function buildQuery(path: string, params: Record<string, string | number>): string {
  const search = new URLSearchParams()
  for (const [key, value] of Object.entries(params)) {
    search.set(key, String(value))
  }
  return `${path}?${search.toString()}`
}

function currentReportPath(): string {
  if (selectedFamily.value === 'sales') {
    return buildQuery('/reports/sales-trends', {
      days: days.value,
      bucket: salesBucket.value,
      metric: salesMetric.value,
    })
  }

  if (selectedFamily.value === 'circulation') {
    if (circulationDataset.value === 'top_titles') {
      return buildQuery('/reports/top-titles', {
        days: days.value,
        limit: topLimit.value,
      })
    }

    return buildQuery('/reports/checkouts-by-genre', {
      days: days.value,
    })
  }

  return buildQuery('/reports/inventory-health', {
    scope: inventoryScope.value,
  })
}

function currentExportPath(): string {
  if (selectedFamily.value === 'sales') {
    return buildQuery('/reports/export.csv', {
      report: 'sales_trends',
      days: days.value,
      bucket: salesBucket.value,
      metric: salesMetric.value,
    })
  }

  if (selectedFamily.value === 'circulation') {
    if (circulationDataset.value === 'top_titles') {
      return buildQuery('/reports/export.csv', {
        report: 'top_titles',
        days: days.value,
        limit: topLimit.value,
      })
    }

    return buildQuery('/reports/export.csv', {
      report: 'checkouts_by_genre',
      days: days.value,
    })
  }

  return buildQuery('/reports/export.csv', {
    report: 'inventory_health',
    scope: inventoryScope.value,
  })
}

async function loadReport(): Promise<void> {
  loading.value = true
  error.value = null
  exportMessage.value = null

  try {
    report.value = await apiFetch<ReportResponse>(currentReportPath())
  } catch (e) {
    if (e instanceof ApiError) {
      error.value = e.message
    } else {
      error.value = String(e)
    }
    report.value = null
  } finally {
    loading.value = false
  }
}

async function exportCurrentReport(): Promise<void> {
  exporting.value = true
  error.value = null
  exportMessage.value = null

  try {
    const res = await fetch(`${getApiBase()}${currentExportPath()}`, {
      method: 'GET',
      credentials: 'include',
    })

    if (!res.ok) {
      let message = `${res.status} ${res.statusText}`
      try {
        const data = await res.json()
        if (typeof data?.detail === 'string') {
          message = data.detail
        }
      } catch {
        // fallback already set
      }
      throw new Error(message)
    }

    const blob = await res.blob()
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    const fileName = `${report.value?.report ?? 'report'}.csv`

    link.href = url
    link.download = fileName
    document.body.appendChild(link)
    link.click()
    link.remove()
    window.URL.revokeObjectURL(url)
    exportMessage.value = `Downloaded ${fileName}`
  } catch (e) {
    error.value = e instanceof Error ? e.message : String(e)
  } finally {
    exporting.value = false
  }
}

const plotSpec = computed(() => {
  if (!report.value) {
    return {
      data: [],
      layout: {},
    }
  }

  const rows = report.value.rows
  const { label_field: labelField, primary_value_field: valueField } = report.value.chart_meta
  const labels = rows.map((row) => String(row[labelField] ?? ''))
  const values = rows.map((row) => Number(row[valueField] ?? 0))
  const baseLayout = {
    title: report.value.title,
    legend: { orientation: 'h' },
    xaxis: { title: report.value.chart_meta.x_title },
    yaxis: { title: report.value.chart_meta.y_title },
  }

  if (selectedStyle.value === 'donut') {
    return {
      data: [
        {
          type: 'pie',
          labels,
          values,
          hole: 0.45,
          textinfo: 'label+percent',
        },
      ],
      layout: {
        ...baseLayout,
        xaxis: undefined,
        yaxis: undefined,
      },
    }
  }

  if (selectedStyle.value === 'bar' || selectedStyle.value === 'timeline') {
    return {
      data: [
        {
          type: 'bar',
          x: labels,
          y: values,
          hovertemplate: '%{x}<br>%{y}<extra></extra>',
        },
      ],
      layout: baseLayout,
    }
  }

  if (selectedStyle.value === 'area') {
    return {
      data: [
        {
          type: 'scatter',
          mode: 'lines+markers',
          x: labels,
          y: values,
          fill: 'tozeroy',
          hovertemplate: '%{x}<br>%{y}<extra></extra>',
        },
      ],
      layout: baseLayout,
    }
  }

  return {
    data: [
      {
        type: 'scatter',
        mode: 'lines+markers',
        x: labels,
        y: values,
        hovertemplate: '%{x}<br>%{y}<extra></extra>',
      },
    ],
    layout: baseLayout,
  }
})

watch(
  () => [
    selectedFamily.value,
    days.value,
    salesBucket.value,
    salesMetric.value,
    circulationDataset.value,
    topLimit.value,
    inventoryScope.value,
  ],
  () => {
    void loadReport()
  },
)

watch(report, (value) => {
  if (!value) return
  if (!value.available_styles.includes(selectedStyle.value)) {
    selectedStyle.value = value.default_style as ChartStyle
  }
})

onMounted(() => {
  void loadReport()
})
</script>

<template>
  <article class="bi-card">
    <div class="bi-heading">
      <div>
        <h2>Business Intelligence Workspace</h2>
        <p class="bi-subtitle">
          Choose a report family, pick a live chart style, then adjust filters to build a dynamic
          Plotly chart.
        </p>
      </div>
    </div>

    <section class="report-family-grid" aria-label="Report families">
      <button
        v-for="family in reportFamilies"
        :key="family.key"
        type="button"
        class="family-card"
        :class="{ active: familyIsActive(family.key) }"
        @click="selectedFamily = family.key"
      >
        <strong>{{ family.label }}</strong>
        <span>{{ family.blurb }}</span>
      </button>
    </section>

    <section class="filter-bar" aria-label="Report filters">
      <label class="filter-control">
        <span>Range</span>
        <select v-model.number="days">
          <option :value="30">Last 30 days</option>
          <option :value="90">Last 90 days</option>
          <option :value="180">Last 180 days</option>
          <option :value="365">Last 12 months</option>
        </select>
      </label>

      <label v-if="selectedFamily === 'sales'" class="filter-control">
        <span>Bucket</span>
        <select v-model="salesBucket">
          <option value="month">Monthly</option>
          <option value="week">Weekly</option>
        </select>
      </label>

      <label v-if="selectedFamily === 'sales'" class="filter-control">
        <span>Metric</span>
        <select v-model="salesMetric">
          <option value="revenue">Revenue</option>
          <option value="quantity">Units Sold</option>
        </select>
      </label>

      <label v-if="selectedFamily === 'circulation'" class="filter-control">
        <span>Dataset</span>
        <select v-model="circulationDataset">
          <option value="checkouts_by_genre">Checkouts by Genre</option>
          <option value="top_titles">Top Titles</option>
        </select>
      </label>

      <label
        v-if="selectedFamily === 'circulation' && circulationDataset === 'top_titles'"
        class="filter-control"
      >
        <span>Top Limit</span>
        <select v-model.number="topLimit">
          <option :value="5">Top 5</option>
          <option :value="10">Top 10</option>
          <option :value="15">Top 15</option>
        </select>
      </label>

      <label v-if="selectedFamily === 'inventory'" class="filter-control">
        <span>Scope</span>
        <select v-model="inventoryScope">
          <option value="all">All Inventory</option>
          <option value="attention_only">Low Stock + Stockout Only</option>
        </select>
      </label>

      <div class="filter-actions">
        <button type="button" @click="loadReport" :disabled="loading">
          {{ loading ? 'Refreshing…' : 'Refresh' }}
        </button>
        <button type="button" @click="exportCurrentReport" :disabled="exporting || loading">
          {{ exporting ? 'Exporting…' : 'Export CSV' }}
        </button>
      </div>
    </section>

    <section class="summary-grid" v-if="report && report.summary.length > 0">
      <article v-for="item in report.summary" :key="item.label" class="summary-chip">
        <span>{{ item.label }}</span>
        <strong>{{ item.value }}</strong>
      </article>
    </section>

    <section class="tile-grid" aria-label="Chart style picker">
      <button
        v-for="tile in chartTiles"
        :key="tile.key"
        type="button"
        class="tile-card"
        :class="{
          selected: selectedStyle === tile.key,
          disabled: styleDisabled(tile),
        }"
        :disabled="styleDisabled(tile)"
        @click="selectStyle(tile)"
      >
        <div class="tile-preview" :style="tilePreviewStyle(tile)"></div>
        <div class="tile-copy">
          <div class="tile-title-row">
            <strong>{{ tile.label }}</strong>
            <span v-if="tile.planned" class="tile-tag muted">Planned</span>
            <span v-else-if="styleDisabled(tile)" class="tile-tag muted">Unavailable</span>
            <span v-else class="tile-tag active-tag">Live</span>
          </div>
          <p>{{ tile.blurb }}</p>
        </div>
      </button>
    </section>

    <p v-if="error" class="error">{{ error }}</p>
    <p v-if="exportMessage" class="success">{{ exportMessage }}</p>

    <section v-if="loading" class="chart-shell empty-state">
      <h3>Loading report…</h3>
      <p>Fetching report data and preparing the chart workspace.</p>
    </section>

    <section v-else-if="report && hasChartData" class="chart-shell">
      <div class="chart-header">
        <div>
          <h3>{{ report.title }}</h3>
          <p>{{ report.description }}</p>
        </div>
      </div>

      <PlotlyChart :data="plotSpec.data" :layout="plotSpec.layout" :loading="loading" />
    </section>

    <section v-else-if="report" class="chart-shell empty-state">
      <h3>{{ report.title }}</h3>
      <p>{{ report.empty_message }}</p>
    </section>

    <section v-if="report && currentTableColumns.length > 0" class="table-shell">
      <div class="chart-header">
        <div>
          <h3>{{ currentDetailRows.length > 0 ? 'Detailed rows' : 'Report data' }}</h3>
          <p>These rows match what will be exported for the current filtered report view.</p>
        </div>
      </div>

      <div class="table-wrap">
        <table>
          <thead>
            <tr>
              <th v-for="column in currentTableColumns" :key="column">{{ column }}</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(row, index) in currentTableRows" :key="`${report.report}-${index}`">
              <td v-for="column in currentTableColumns" :key="column">
                {{ displayValue(column, row[column]) }}
              </td>
            </tr>
            <tr v-if="currentTableRows.length === 0">
              <td :colspan="currentTableColumns.length" class="empty-row">
                No rows match the current report filters.
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>
  </article>
</template>

<style scoped>
.bi-card {
  border: 1px solid #8080805f;
  border-radius: 10px;
  padding: 16px;
  background: var(--color-background);
}

.bi-heading {
  margin-bottom: 16px;
}

.bi-heading h2 {
  color: #c89600;
  margin-bottom: 4px;
}

.bi-subtitle {
  opacity: 0.82;
}

.report-family-grid,
.tile-grid,
.summary-grid,
.filter-bar {
  display: grid;
  gap: 12px;
}

.report-family-grid {
  grid-template-columns: 1fr;
  margin-bottom: 16px;
}

.family-card,
.tile-card,
.summary-chip {
  border: 1px solid #8080805f;
  border-radius: 12px;
  /* background: var(--color-background); */
}

.family-card {
  text-align: left;
  padding: 12px;
  cursor: pointer;
  transition:
    transform 0.18s ease,
    border-color 0.18s ease,
    box-shadow 0.18s ease;
}

.family-card strong {
  display: block;
  margin-bottom: 4px;
}

.family-card span {
  opacity: 0.82;
}

.family-card.active,
.tile-card.selected {
  border-color: #c89600;
  box-shadow: 0 0 0 2px rgba(200, 150, 0, 0.18);
}

.filter-bar {
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  align-items: end;
  margin-bottom: 16px;
}

.filter-control {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.filter-control span {
  font-size: 0.92rem;
  opacity: 0.82;
}

.filter-control select,
.filter-actions button {
  padding: 8px 10px;
  border: 1px solid #8080805f;
  border-radius: 8px;
  background: var(--color-background);
}

.filter-actions {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.filter-actions button,
.tile-card,
.family-card {
  cursor: pointer;
}

.summary-grid {
  grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
  margin-bottom: 16px;
}

.summary-chip {
  padding: 12px;
}

.summary-chip span {
  display: block;
  opacity: 0.8;
  font-size: 0.92rem;
}

.summary-chip strong {
  font-size: 1.1rem;
}

.tile-grid {
  grid-template-columns: 1fr;
  margin-bottom: 16px;
}

.tile-card {
  padding: 0;
  overflow: hidden;
  transition:
    transform 0.18s ease,
    box-shadow 0.18s ease,
    border-color 0.18s ease;
}

.tile-card:hover:not(.disabled),
.family-card:hover {
  transform: translateY(-2px) scale(1.01);
}

.tile-card.disabled {
  opacity: 0.58;
  cursor: not-allowed;
}

.tile-preview {
  width: 100%;
  height: 160px;
  background-repeat: no-repeat;
  border-bottom: 1px solid #8080805f;
}

.tile-copy {
  padding: 12px;
  text-align: left;
}

.tile-copy p {
  margin-top: 6px;
  opacity: 0.82;
}

.tile-title-row {
  display: flex;
  justify-content: space-between;
  gap: 10px;
  align-items: center;
}

.tile-tag {
  border-radius: 999px;
  padding: 2px 10px;
  font-size: 0.8rem;
}

.tile-tag.muted {
  background: #ececec;
}

.tile-tag.active-tag {
  background: #fff1cc;
}

.chart-shell,
.table-shell {
  border: 1px solid #8080805f;
  border-radius: 12px;
  padding: 16px;
  background: rgba(255, 255, 255, 0.35);
}

.chart-shell {
  margin-bottom: 16px;
}

.chart-header {
  margin-bottom: 10px;
}

.chart-header h3 {
  margin-bottom: 4px;
}

.table-wrap {
  width: 100%;
  overflow-x: auto;
}

.table-wrap table {
  width: 100%;
  border-collapse: collapse;
  min-width: 640px;
}

.table-wrap th,
.table-wrap td {
  border: 1px solid #8080805f;
  padding: 8px;
  text-align: left;
  vertical-align: top;
}

.empty-state,
.empty-row {
  text-align: center;
}

.error {
  color: #c00;
  margin-bottom: 12px;
}

.success {
  color: #0a7a2f;
  margin-bottom: 12px;
}

@media (min-width: 760px) {
  .report-family-grid {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }

  .tile-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (min-width: 1180px) {
  .tile-grid {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }
}
</style>
