<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { RouterLink } from 'vue-router'
import BusinessIntelWorkspace from '@/components/BusinessIntelWorkspace.vue'
import PageHeader from '@/components/PageHeader.vue'
import { apiFetch, ApiError } from '@/lib/api'

type Location = { aisle: string; shelf: string }

type LowStockItem = {
  book_id: number
  title: string
  isbn: string
  on_hand: number
  threshold: number
  location: Location | null
}

type LowStockResponse = {
  default_threshold: number
  low_stock: LowStockItem[]
  stockout: LowStockItem[]
}

type LoanStatus = 'active' | 'due_soon' | 'overdue' | 'returned'

type LoanOut = {
  id: number
  created_at: string
  due_date: string
  returned_at: string | null
  status: LoanStatus
  due_soon: boolean
  days_until_due: number | null
  member: {
    id: number
    name: string
    email: string
  }
  book: {
    id: number
    title: string
    isbn: string
    edition: number
  }
}

const loading = ref(true)
const error = ref<string | null>(null)

const inventoryData = ref<LowStockResponse | null>(null)
const overdueLoans = ref<LoanOut[]>([])
const dueSoonLoans = ref<LoanOut[]>([])

const dueSoonWindowDays = 7
const panelLoanLimit = 5

const lowStockRows = computed(() => inventoryData.value?.low_stock ?? [])
const stockoutRows = computed(() => inventoryData.value?.stockout ?? [])

function statusLabel(status: LoanStatus): string {
  switch (status) {
    case 'due_soon':
      return 'Due Soon'
    case 'overdue':
      return 'Overdue'
    case 'returned':
      return 'Returned'
    default:
      return 'Active'
  }
}

function dueText(loan: LoanOut): string {
  if (loan.days_until_due === null) return '—'
  if (loan.status === 'overdue') return `${Math.abs(loan.days_until_due)} day(s) late`
  if (loan.days_until_due === 0) return 'Due today'
  return `${loan.days_until_due} day(s)`
}

async function loadDashboard(): Promise<void> {
  loading.value = true
  error.value = null

  try {
    const [inventory, overdue, dueSoon] = await Promise.all([
      apiFetch<LowStockResponse>('/dashboard/low-stock'),
      apiFetch<LoanOut[]>(`/loans?overdue_only=true&offset=0&limit=${panelLoanLimit}`),
      apiFetch<LoanOut[]>(
        `/loans?due_soon_only=true&due_within_days=${dueSoonWindowDays}&offset=0&limit=${panelLoanLimit}`,
      ),
    ])

    inventoryData.value = inventory
    overdueLoans.value = overdue
    dueSoonLoans.value = dueSoon
  } catch (e) {
    if (e instanceof ApiError) {
      error.value = e.message
    } else {
      error.value = String(e)
    }
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  void loadDashboard()
})
</script>

<template>
  <PageHeader page="Dashboard" />

  <main class="page">
    <p v-if="loading">Loading dashboard...</p>
    <p v-else-if="error" class="error">Error: {{ error }}</p>

    <section v-else-if="inventoryData" class="dashboard-shell">
      <section class="panel-grid">
        <article class="panel-card">
          <div class="panel-header">
            <div>
              <h2>Stockout</h2>
              <p class="panel-subtitle">Books currently at zero on-hand.</p>
            </div>
            <RouterLink class="panel-link" to="/inventory">Open Inventory</RouterLink>
          </div>

          <div class="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Title</th>
                  <th>On Hand</th>
                  <th>Location</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="item in stockoutRows" :key="`stockout-${item.book_id}`">
                  <td class="title-cell">
                    <span class="title-text" :title="item.title">{{ item.title }}</span>
                  </td>
                  <td>{{ item.on_hand }}</td>
                  <td>
                    {{
                      item.location ? `${item.location.aisle}-${item.location.shelf}` : 'Unassigned'
                    }}
                  </td>
                </tr>
                <tr v-if="stockoutRows.length === 0">
                  <td colspan="3" class="empty">No stockout titles</td>
                </tr>
              </tbody>
            </table>
          </div>
        </article>

        <article class="panel-card">
          <div class="panel-header">
            <div>
              <h2>Low Stock</h2>
              <p class="panel-subtitle">Titles at or below their set threshold.</p>
            </div>
            <RouterLink class="panel-link" to="/inventory">Open Inventory</RouterLink>
          </div>

          <div class="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Title</th>
                  <th>On Hand</th>
                  <th>Threshold</th>
                  <th>Location</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="item in lowStockRows" :key="`low-${item.book_id}`">
                  <td class="title-cell">
                    <span class="title-text" :title="item.title">{{ item.title }}</span>
                  </td>
                  <td>{{ item.on_hand }}</td>
                  <td>{{ item.threshold }}</td>
                  <td>
                    {{
                      item.location ? `${item.location.aisle}-${item.location.shelf}` : 'Unassigned'
                    }}
                  </td>
                </tr>
                <tr v-if="lowStockRows.length === 0">
                  <td colspan="4" class="empty">No low-stock titles</td>
                </tr>
              </tbody>
            </table>
          </div>
        </article>

        <article class="panel-card">
          <div class="panel-header">
            <div>
              <h2>Overdue</h2>
              <p class="panel-subtitle">Active loans already past due.</p>
            </div>
            <RouterLink class="panel-link" to="/returns">Open Returns</RouterLink>
          </div>

          <div class="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Title</th>
                  <th>Member</th>
                  <th>Due Date</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="loan in overdueLoans" :key="`overdue-${loan.id}`">
                  <td class="title-cell">
                    <span class="title-text" :title="loan.book.title">{{ loan.book.title }}</span>
                  </td>
                  <td>{{ loan.member.name }}</td>
                  <td>{{ loan.due_date }}</td>
                  <td>
                    <span class="status-pill overdue">
                      {{ statusLabel(loan.status) }} · {{ dueText(loan) }}
                    </span>
                  </td>
                </tr>
                <tr v-if="overdueLoans.length === 0">
                  <td colspan="4" class="empty">No overdue loans</td>
                </tr>
              </tbody>
            </table>
          </div>
        </article>

        <article class="panel-card">
          <div class="panel-header">
            <div>
              <h2>Due Soon</h2>
              <p class="panel-subtitle">
                Active loans due within the next {{ dueSoonWindowDays }} days.
              </p>
            </div>
            <RouterLink class="panel-link" to="/returns">Open Returns</RouterLink>
          </div>

          <div class="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>Title</th>
                  <th>Member</th>
                  <th>Due Date</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="loan in dueSoonLoans" :key="`due-soon-${loan.id}`">
                  <td class="title-cell">
                    <span class="title-text" :title="loan.book.title">{{ loan.book.title }}</span>
                  </td>
                  <td>{{ loan.member.name }}</td>
                  <td>{{ loan.due_date }}</td>
                  <td>
                    <span class="status-pill due-soon">
                      {{ statusLabel(loan.status) }} · {{ dueText(loan) }}
                    </span>
                  </td>
                </tr>
                <tr v-if="dueSoonLoans.length === 0">
                  <td colspan="4" class="empty">No loans due soon</td>
                </tr>
              </tbody>
            </table>
          </div>
        </article>
      </section>

      <BusinessIntelWorkspace />
    </section>
  </main>
</template>

<style scoped>
.page {
  padding: 24px;
}

.error {
  color: #c00;
}

.dashboard-shell {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.panel-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 16px;
}

.panel-card,
.chart-card {
  border: 1px solid #8080805f;
  border-radius: 10px;
  padding: 16px;
  background: var(--color-background);
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 12px;
  margin-bottom: 12px;
}

.panel-header h2 {
  color: #c89600;
  margin-bottom: 4px;
}

.panel-subtitle {
  opacity: 0.8;
  font-size: 0.95rem;
}

.panel-link {
  white-space: nowrap;
  font-size: 0.95rem;
}

.table-wrap {
  width: 100%;
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
}

table {
  width: 100%;
  border-collapse: collapse;
  table-layout: fixed;
}

th,
td {
  border: 1px solid #8080805f;
  padding: 8px;
  text-align: left;
  vertical-align: top;
}

.title-cell {
  width: 42%;
}

.title-text {
  display: block;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  max-width: 140px;
}

.status-pill {
  display: inline-block;
  padding: 2px 10px;
  border-radius: 999px;
  font-size: 0.9rem;
}

.status-pill.overdue {
  background: #ffd9d9;
  color: #8a0000;
  font-weight: 700;
}

.status-pill.due-soon {
  background: #fff1cc;
}

.empty {
  text-align: center;
  padding: 16px;
}

@media (min-width: 1024px) {
  .panel-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .title-text {
    max-width: 180px;
  }
}

@media (min-width: 1280px) {
  .title-text {
    max-width: 260px;
  }
}

@media (min-width: 1440px) {
  .title-text {
    max-width: 340px;
  }
}
</style>
