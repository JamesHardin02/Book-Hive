<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import PageHeader from '@/components/PageHeader.vue'
import { apiFetch, ApiError } from '@/lib/api'

type LoanOut = {
  id: number
  created_at: string
  due_date: string
  returned_at: string | null
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

function isOverdue(loan: LoanOut): boolean {
  if (loan.returned_at) return false

  const today = new Date()
  const due = new Date(`${loan.due_date}T00:00:00`)
  return due < new Date(today.getFullYear(), today.getMonth(), today.getDate())
}

async function fetchLoans(): Promise<void> {
  loading.value = true
  error.value = null

  try {
    const params = new URLSearchParams()
    params.set('active_only', 'true')
    params.set('overdue_only', overdueOnly.value ? 'true' : 'false')
    params.set('offset', '0')
    params.set('limit', '50')

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

  return loans.value.filter((loan) => {
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
})

function clearFilters(): void {
  memberFilter.value = ''
  bookFilter.value = ''
  dueDateFilter.value = ''
  overdueOnly.value = false
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
  <PageHeader page="Returns" />

  <main class="page">
    <section class="card">
      <h2>Process Returns</h2>

      <div class="toolbar">
        <input v-model="memberFilter" type="text" placeholder="Filter by member" />
        <input v-model="bookFilter" type="text" placeholder="Filter by book or ISBN" />
        <input v-model="dueDateFilter" type="text" placeholder="Due date (YYYY-MM-DD)" />

        <label class="checkbox">
          <input v-model="overdueOnly" type="checkbox" @change="fetchLoans" />
          Overdue only
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
              <th>Created</th>
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
                <span v-if="isOverdue(loan)" class="overdue">Overdue</span>
                <span v-else>Active</span>
              </td>
              <td>{{ loan.created_at }}</td>
              <td>
                <button type="button" @click="returnLoan(loan)" :disabled="returningId === loan.id">
                  {{ returningId === loan.id ? 'Returning…' : 'Return' }}
                </button>
              </td>
            </tr>

            <tr v-if="!loading && filteredLoans.length === 0">
              <td colspan="8" class="empty">No active loans found</td>
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
  flex-wrap: wrap;
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

.error {
  color: #c00;
  margin-bottom: 10px;
}

.success {
  color: #0a7a2f;
  margin-bottom: 10px;
}

.overdue {
  color: #c00;
  font-weight: 700;
}

.muted {
  opacity: 0.8;
  font-size: 0.92rem;
}

.empty {
  text-align: center;
  padding: 16px;
}

@media (min-width: 768px) {
  .tool-btns {
    flex-wrap: nowrap;
  }
}

@media (min-width: 1024px) {
  .toolbar {
    flex-wrap: nowrap;
  }

  .checkbox {
    width: 350px;
  }

  button {
    max-width: 150px;
  }
}
</style>
