<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import PageHeader from '@/components/PageHeader.vue'
import { apiFetch, ApiError } from '@/lib/api'

type LoanStatus = 'active' | 'due_soon' | 'overdue' | 'returned'

const DUE_SOON_DAYS = 7

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

const loans = ref<LoanOut[]>([])
const loading = ref(false)
const error = ref<string | null>(null)
const successMessage = ref<string | null>(null)
const returningId = ref<number | null>(null)

const memberFilter = ref('')
const bookFilter = ref('')
const dueDateFilter = ref('')
const overdueOnly = ref(false)
const dueSoonOnly = ref(false)
const includeReturned = ref(false)

const summary = computed(() => ({
  active: loans.value.filter((loan) => loan.status === 'active').length,
  dueSoon: loans.value.filter((loan) => loan.status === 'due_soon').length,
  overdue: loans.value.filter((loan) => loan.status === 'overdue').length,
  returned: loans.value.filter((loan) => loan.status === 'returned').length,
}))

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

async function fetchLoans(): Promise<void> {
  loading.value = true
  error.value = null

  try {
    const params = new URLSearchParams()
    params.set('active_only', includeReturned.value ? 'false' : 'true')
    params.set('overdue_only', overdueOnly.value ? 'true' : 'false')
    params.set('due_soon_only', dueSoonOnly.value ? 'true' : 'false')
    params.set('due_within_days', String(DUE_SOON_DAYS))
    params.set('offset', '0')
    params.set('limit', '100')

    loans.value = await apiFetch<LoanOut[]>(`/loans?${params.toString()}`)
  } catch (e) {
    if (e instanceof ApiError) error.value = e.message
    else error.value = String(e)
    loans.value = []
  } finally {
    loading.value = false
  }
}

const filteredLoans = computed(() => {
  const member = memberFilter.value.trim().toLowerCase()
  const book = bookFilter.value.trim().toLowerCase()
  const due = dueDateFilter.value.trim()

  return [...loans.value]
    .filter((loan) => {
      if (member) {
        const memberMatch =
          loan.member.name.toLowerCase().includes(member) ||
          loan.member.email.toLowerCase().includes(member)
        if (!memberMatch) return false
      }

      if (book) {
        const bookMatch =
          loan.book.title.toLowerCase().includes(book) || loan.book.isbn.includes(book)
        if (!bookMatch) return false
      }

      if (due && !loan.due_date.includes(due)) return false

      return true
    })
    .sort((a, b) => {
      const aTime = new Date(`${a.due_date}T00:00:00`).getTime()
      const bTime = new Date(`${b.due_date}T00:00:00`).getTime()
      return aTime - bTime || a.id - b.id
    })
})

function clearFilters(): void {
  memberFilter.value = ''
  bookFilter.value = ''
  dueDateFilter.value = ''
  overdueOnly.value = false
  dueSoonOnly.value = false
  includeReturned.value = false
  fetchLoans()
}

function toggleOverdueOnly(): void {
  if (overdueOnly.value) dueSoonOnly.value = false
  fetchLoans()
}

function toggleDueSoonOnly(): void {
  if (dueSoonOnly.value) overdueOnly.value = false
  fetchLoans()
}

async function returnLoan(loan: LoanOut): Promise<void> {
  error.value = null
  successMessage.value = null
  returningId.value = loan.id

  try {
    const returned = await apiFetch<LoanOut>(`/loans/${loan.id}/return`, {
      method: 'PATCH',
    })

    successMessage.value = `Returned "${returned.book.title}" from ${returned.member.name}.`
    await fetchLoans()
  } catch (e) {
    if (e instanceof ApiError) error.value = e.message
    else error.value = String(e)
  } finally {
    returningId.value = null
  }
}

onMounted(() => {
  fetchLoans()
})
</script>

<template>
  <PageHeader page="Returns & Loan Status" />

  <main class="page">
    <section class="card">
      <h2>Due / Overdue Loans</h2>
      <p class="hint">Due soon means a loan due within the next {{ DUE_SOON_DAYS }} days.</p>

      <div class="summary-grid">
        <article class="summary-card">
          <span class="summary-label">Active</span>
          <strong>{{ summary.active }}</strong>
        </article>
        <article class="summary-card">
          <span class="summary-label">Due Soon</span>
          <strong>{{ summary.dueSoon }}</strong>
        </article>
        <article class="summary-card">
          <span class="summary-label">Overdue</span>
          <strong>{{ summary.overdue }}</strong>
        </article>
        <article class="summary-card">
          <span class="summary-label">Returned</span>
          <strong>{{ summary.returned }}</strong>
        </article>
      </div>

      <div class="toolbar">
        <input v-model="memberFilter" type="text" placeholder="Filter by member" />
        <input v-model="bookFilter" type="text" placeholder="Filter by book or ISBN" />
        <input v-model="dueDateFilter" type="text" placeholder="Due date (YYYY-MM-DD)" />

        <label class="checkbox">
          <input v-model="dueSoonOnly" type="checkbox" @change="toggleDueSoonOnly" />
          Due soon only
        </label>

        <label class="checkbox">
          <input v-model="overdueOnly" type="checkbox" @change="toggleOverdueOnly" />
          Overdue only
        </label>

        <label class="checkbox">
          <input v-model="includeReturned" type="checkbox" @change="fetchLoans" />
          Include returned
        </label>

        <div class="tool-btns">
          <button type="button" @click="fetchLoans" :disabled="loading">
            {{ loading ? 'Loading…' : 'Refresh' }}
          </button>
          <button type="button" @click="clearFilters" :disabled="loading">Clear</button>
        </div>
      </div>

      <p v-if="error" class="error">{{ error }}</p>
      <p v-if="successMessage" class="success">{{ successMessage }}</p>

      <div class="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Book</th>
              <th>ISBN</th>
              <th>Edition</th>
              <th>Member</th>
              <th>Due Date</th>
              <th>Status</th>
              <th>Days Until Due</th>
              <th>Created</th>
              <th>Returned</th>
              <th>Return</th>
            </tr>
          </thead>

          <tbody>
            <tr v-for="loan in filteredLoans" :key="loan.id">
              <td>{{ loan.book.title }}</td>
              <td>{{ loan.book.isbn }}</td>
              <td>{{ loan.book.edition }}</td>
              <td>
                <div>{{ loan.member.name }}</div>
                <div class="muted">{{ loan.member.email }}</div>
              </td>
              <td>{{ loan.due_date }}</td>
              <td>
                <span class="status-pill" :class="loan.status">
                  {{ statusLabel(loan.status) }}
                </span>
              </td>
              <td>{{ dueText(loan) }}</td>
              <td>{{ loan.created_at }}</td>
              <td>{{ loan.returned_at ?? '—' }}</td>
              <td>
                <button
                  type="button"
                  @click="returnLoan(loan)"
                  :disabled="loan.status === 'returned' || returningId === loan.id"
                >
                  {{ returningId === loan.id ? 'Returning…' : 'Return' }}
                </button>
              </td>
            </tr>

            <tr v-if="!loading && filteredLoans.length === 0">
              <td colspan="10" class="empty">No loans match the current filters</td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>
  </main>
</template>

<style scoped>
.page {
  padding: 24px;
}

.card {
  border: 1px solid #8080805f;
  border-radius: 10px;
  padding: 16px;
  background: var(--color-background);
}

.hint {
  margin-bottom: 12px;
  opacity: 0.85;
}

.summary-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
  gap: 12px;
  margin-bottom: 16px;
}

.summary-card {
  border: 1px solid #8080805f;
  border-radius: 8px;
  padding: 12px;
}

.summary-label {
  display: block;
  font-size: 0.9rem;
  opacity: 0.8;
  margin-bottom: 4px;
}

.toolbar {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  align-items: center;
  margin-bottom: 16px;
}

.toolbar input {
  padding: 8px;
  border: 1px solid #8080805f;
  border-radius: 6px;
}

.tool-btns {
  display: flex;
  width: 100%;
  gap: 16px;
}

.checkbox {
  display: flex;
  align-items: center;
  gap: 6px;
}

.table-wrap {
  width: 100%;
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
}

table {
  min-width: 1100px;
  width: 100%;
  border-collapse: collapse;
}

th,
td {
  border: 1px solid #8080805f;
  padding: 8px;
  text-align: left;
  vertical-align: top;
}

button {
  padding: 8px 12px;
  border: none;
  border-radius: 6px;
  background: var(--vt-c-indigo);
  color: white;
  cursor: pointer;
}

button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.status-pill {
  display: inline-block;
  padding: 2px 10px;
  border-radius: 999px;
  font-size: 0.9rem;
}

.status-pill.active {
  background: #e6f0ff;
}

.status-pill.due_soon {
  background: #fff1cc;
  width: max-content;
}

.status-pill.overdue {
  background: #ffd9d9;
  color: #8a0000;
  font-weight: 700;
}

.status-pill.returned {
  background: #e7f7ea;
  color: #0a7a2f;
}

.muted {
  opacity: 0.8;
  font-size: 0.92rem;
}

.error {
  color: #c00;
}

.success {
  color: #0a7a2f;
}

.empty {
  text-align: center;
  padding: 16px;
}

@media (min-width: 640px) {
  .tool-btns > button {
    max-width: 150px;
  }
}
</style>
