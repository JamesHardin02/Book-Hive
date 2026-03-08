<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import PageHeader from '@/components/PageHeader.vue'
import { apiFetch, ApiError } from '@/lib/api'

type MemberOut = {
  id: number
  name: string
  email: string
  phone_number: string
  created_at: string
}

type LocationOut = {
  id: number
  aisle: string
  shelf: string
}

type InventoryOut = {
  book_id: number
  on_hand: number
  min_threshold?: number | null
  location?: LocationOut | null
}

type BookOut = {
  id: number
  isbn: string
  edition: number
  title: string
  author: string
  genre: string
  year: number
  unit_price: number | string | null
  cover_url: string | null
  created_at: string
  inventory?: InventoryOut | null
}

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

const memberName = ref('')
const memberEmail = ref('')
const bookTitle = ref('')
const bookIsbn = ref('')

const members = ref<MemberOut[]>([])
const books = ref<BookOut[]>([])
const loans = ref<LoanOut[]>([])

const selectedMemberId = ref<number | null>(null)
const selectedBookId = ref<number | null>(null)

const dueDate = ref(defaultDueDate())

const loadingMembers = ref(false)
const loadingBooks = ref(false)
const loadingLoans = ref(false)
const submitting = ref(false)

const error = ref<string | null>(null)
const successMessage = ref<string | null>(null)

function defaultDueDate(): string {
  const d = new Date()
  d.setDate(d.getDate() + 14)
  return d.toISOString().slice(0, 10)
}

function normalizeIsbn(s: string): string {
  return s.replace(/[^0-9]/g, '')
}

const selectedMember = computed(
  () => members.value.find((m) => m.id === selectedMemberId.value) ?? null,
)

const selectedBook = computed(() => books.value.find((b) => b.id === selectedBookId.value) ?? null)

async function searchMembers(): Promise<void> {
  loadingMembers.value = true
  error.value = null

  try {
    const params = new URLSearchParams()
    if (memberName.value.trim()) params.set('name', memberName.value.trim())
    if (memberEmail.value.trim()) params.set('email', memberEmail.value.trim())
    params.set('offset', '0')
    params.set('limit', '25')

    members.value = await apiFetch<MemberOut[]>(`/members?${params.toString()}`)
  } catch (e) {
    if (e instanceof ApiError) error.value = e.message
    else error.value = String(e)
    members.value = []
  } finally {
    loadingMembers.value = false
  }
}

async function searchBooks(): Promise<void> {
  loadingBooks.value = true
  error.value = null

  try {
    const params = new URLSearchParams()
    if (bookTitle.value.trim()) params.set('title', bookTitle.value.trim())
    if (bookIsbn.value.trim()) params.set('isbn', normalizeIsbn(bookIsbn.value.trim()))
    params.set('offset', '0')
    params.set('limit', '25')

    books.value = await apiFetch<BookOut[]>(`/books?${params.toString()}`)
  } catch (e) {
    if (e instanceof ApiError) error.value = e.message
    else error.value = String(e)
    books.value = []
  } finally {
    loadingBooks.value = false
  }
}

async function fetchActiveLoans(): Promise<void> {
  loadingLoans.value = true

  try {
    loans.value = await apiFetch<LoanOut[]>('/loans?active_only=true&offset=0&limit=25')
  } catch (e) {
    if (e instanceof ApiError) error.value = e.message
    else error.value = String(e)
    loans.value = []
  } finally {
    loadingLoans.value = false
  }
}

function selectMember(memberId: number): void {
  selectedMemberId.value = memberId
}

function selectBook(bookId: number): void {
  selectedBookId.value = bookId
}

async function submitCheckout(e: Event): Promise<void> {
  e.preventDefault()
  error.value = null
  successMessage.value = null

  if (selectedMemberId.value === null) {
    error.value = 'Please select a member.'
    return
  }

  if (selectedBookId.value === null) {
    error.value = 'Please select a book.'
    return
  }

  if (!dueDate.value) {
    error.value = 'Please choose a due date.'
    return
  }

  submitting.value = true

  try {
    const created = await apiFetch<LoanOut>('/loans', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        member_id: selectedMemberId.value,
        book_id: selectedBookId.value,
        due_date: dueDate.value,
      }),
    })

    successMessage.value = `Checked out "${created.book.title}" to ${created.member.name}.`
    await searchBooks()
    await fetchActiveLoans()
  } catch (e) {
    if (e instanceof ApiError) error.value = e.message
    else error.value = String(e)
  } finally {
    submitting.value = false
  }
}

onMounted(() => {
  fetchActiveLoans()
})
</script>

<template>
  <PageHeader page="Checkout" :booksearch="false" />

  <main class="page">
    <section class="card">
      <h2>Find Member</h2>

      <div class="toolbar">
        <input v-model="memberName" type="text" placeholder="Member name" />
        <input v-model="memberEmail" type="text" placeholder="Member email" />
        <button type="button" @click="searchMembers" :disabled="loadingMembers">
          {{ loadingMembers ? 'Searching…' : 'Search Members' }}
        </button>
      </div>

      <div class="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Name</th>
              <th>Email</th>
              <th>Phone</th>
              <th>Select</th>
            </tr>
          </thead>

          <tbody>
            <tr v-for="m in members" :key="m.id">
              <td>{{ m.name }}</td>
              <td>{{ m.email }}</td>
              <td>{{ m.phone_number }}</td>
              <td>
                <button type="button" @click="selectMember(m.id)">
                  {{ selectedMemberId === m.id ? 'Selected' : 'Select' }}
                </button>
              </td>
            </tr>

            <tr v-if="!loadingMembers && members.length === 0">
              <td colspan="4" class="empty">No members loaded</td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>

    <section class="card">
      <h2>Find Book</h2>

      <div class="toolbar">
        <input v-model="bookTitle" type="text" placeholder="Book title" />
        <input v-model="bookIsbn" type="text" placeholder="ISBN" />
        <button type="button" @click="searchBooks" :disabled="loadingBooks">
          {{ loadingBooks ? 'Searching…' : 'Search Books' }}
        </button>
      </div>

      <div class="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Title</th>
              <th>Author</th>
              <th>Subject</th>
              <th>ISBN</th>
              <th>On-Hand</th>
              <th>Location</th>
              <th>Select</th>
            </tr>
          </thead>

          <tbody>
            <tr v-for="b in books" :key="b.id">
              <td>{{ b.title }}</td>
              <td>{{ b.author }}</td>
              <td>{{ b.genre }}</td>
              <td>{{ b.isbn }}</td>
              <td>{{ b.inventory?.on_hand ?? 0 }}</td>
              <td>
                <span v-if="b.inventory?.location">
                  {{ b.inventory.location.aisle }} / {{ b.inventory.location.shelf }}
                </span>
                <span v-else>—</span>
              </td>
              <td>
                <button
                  type="button"
                  @click="selectBook(b.id)"
                  :disabled="(b.inventory?.on_hand ?? 0) <= 0"
                >
                  {{ selectedBookId === b.id ? 'Selected' : 'Select' }}
                </button>
              </td>
            </tr>

            <tr v-if="!loadingBooks && books.length === 0">
              <td colspan="7" class="empty">No books loaded</td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>

    <p v-if="error" class="error">{{ error }}</p>
    <p v-if="successMessage" class="success">{{ successMessage }}</p>

    <section class="card">
      <h2>Checkout Loan</h2>

      <form class="checkout-form" @submit="submitCheckout">
        <div class="selection-summary">
          <div>
            <strong>Selected Member:</strong>
            <span v-if="selectedMember">
              {{ selectedMember.name }} ({{ selectedMember.email }})
            </span>
            <span v-else>None selected</span>
          </div>

          <div>
            <strong>Selected Book:</strong>
            <span v-if="selectedBook">
              {{ selectedBook.title }} — On-Hand:
              {{ selectedBook.inventory?.on_hand ?? 0 }}
            </span>
            <span v-else>None selected</span>
          </div>
        </div>

        <div class="submission">
          <label>
            Due Date
            <input v-model="dueDate" type="date" required />
          </label>

          <button type="submit" :disabled="submitting">
            {{ submitting ? 'Checking Out…' : 'Create Checkout' }}
          </button>
        </div>
      </form>
    </section>

    <section class="card">
      <h2>Active Loans</h2>

      <p v-if="loadingLoans">Loading active loans…</p>

      <div class="table-wrap" v-else>
        <table>
          <thead>
            <tr>
              <th>Book</th>
              <th>Member</th>
              <th>Due Date</th>
              <th>Created</th>
            </tr>
          </thead>

          <tbody>
            <tr v-for="loan in loans" :key="loan.id">
              <td>{{ loan.book.title }}</td>
              <td>{{ loan.member.name }}</td>
              <td>{{ loan.due_date }}</td>
              <td>{{ loan.created_at }}</td>
            </tr>

            <tr v-if="loans.length === 0">
              <td colspan="4" class="empty">No active loans</td>
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
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.card {
  border: 1px solid #8080805f;
  border-radius: 10px;
  padding: 16px;
  background: var(--color-background);
}

.checkout-form {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.selection-summary {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.toolbar {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  margin-bottom: 12px;
}

.toolbar input,
.checkout-form input {
  padding: 8px;
  border: 1px solid #8080805f;
  border-radius: 6px;
}

.table-wrap {
  width: 100%;
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
}

table {
  min-width: 900px;
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
}

.success {
  color: #0a7a2f;
}

.empty {
  text-align: center;
  padding: 16px;
}

@media (min-width: 430px) {
  .submission {
    display: flex;
    gap: 8px;
  }

  .submission > button,
  .toolbar > button {
    max-width: 150px;
  }
}

@media (min-width: 768px) {
  .toolbar {
    flex-wrap: nowrap;
  }
}
</style>
