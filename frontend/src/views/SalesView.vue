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

type SaleOut = {
  id: number
  quantity: number
  unit_price: number | string
  sold_at: string
  book: {
    id: number
    title: string
    isbn: string
    edition: number
  }
  member: {
    id: number
    name: string
    email: string
  } | null
}

const memberName = ref('')
const memberEmail = ref('')
const bookTitle = ref('')
const bookIsbn = ref('')

const members = ref<MemberOut[]>([])
const books = ref<BookOut[]>([])
const sales = ref<SaleOut[]>([])

const selectedMemberId = ref<number | null>(null)
const selectedBookId = ref<number | null>(null)

const quantity = ref(1)
const unitPrice = ref(0)

const loadingMembers = ref(false)
const loadingBooks = ref(false)
const loadingSales = ref(false)
const submitting = ref(false)

const error = ref<string | null>(null)
const successMessage = ref<string | null>(null)

const saleBookFilter = ref('')
const saleMemberFilter = ref('')
const saleDateFilter = ref('')

function normalizeIsbn(s: string): string {
  return s.replace(/[^0-9]/g, '')
}

function toNumberOrNull(v: number): number | null {
  if (!v) return null
  return Number.isFinite(v) ? v : null
}

const selectedMember = computed(
  () => members.value.find((m) => m.id === selectedMemberId.value) ?? null,
)

const selectedBook = computed(() => books.value.find((b) => b.id === selectedBookId.value) ?? null)

const filteredSales = computed(() => {
  const bf = saleBookFilter.value.trim().toLowerCase()
  const mf = saleMemberFilter.value.trim().toLowerCase()
  const df = saleDateFilter.value.trim()

  return sales.value.filter((sale) => {
    if (bf) {
      const match =
        sale.book.title.toLowerCase().includes(bf) || sale.book.isbn.toLowerCase().includes(bf)
      if (!match) return false
    }

    if (mf) {
      const memberText = sale.member
        ? `${sale.member.name} ${sale.member.email}`.toLowerCase()
        : 'walk-in guest'
      if (!memberText.includes(mf)) return false
    }

    if (df && !sale.sold_at.includes(df)) return false

    return true
  })
})

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

async function fetchSales(): Promise<void> {
  loadingSales.value = true
  error.value = null

  try {
    sales.value = await apiFetch<SaleOut[]>('/sales?offset=0&limit=25')
  } catch (e) {
    if (e instanceof ApiError) error.value = e.message
    else error.value = String(e)
    sales.value = []
  } finally {
    loadingSales.value = false
  }
}

function selectMember(memberId: number): void {
  selectedMemberId.value = memberId
}

function clearSelectedMember(): void {
  selectedMemberId.value = null
}

function selectBook(bookId: number): void {
  selectedBookId.value = bookId

  const found = books.value.find((b) => b.id === bookId)
  if (found && found.unit_price !== null) {
    unitPrice.value = Number(found.unit_price)
  }
}

function clearSelectedBook(): void {
  selectedBookId.value = null
}

async function submitSale(e: Event): Promise<void> {
  e.preventDefault()
  error.value = null
  successMessage.value = null

  if (selectedBookId.value === null) {
    error.value = 'Please select a book.'
    return
  }

  const qty = toNumberOrNull(quantity.value)
  if (qty === null || qty < 1) {
    error.value = 'Quantity must be at least 1.'
    return
  }

  const price = toNumberOrNull(unitPrice.value)
  if (price === null || price < 0) {
    error.value = 'Please enter a valid unit price.'
    return
  }

  submitting.value = true

  try {
    const created = await apiFetch<SaleOut>('/sales', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        book_id: selectedBookId.value,
        member_id: selectedMemberId.value,
        quantity: qty,
        unit_price: price,
      }),
    })

    successMessage.value = `Recorded sale of "${created.book.title}" (${created.quantity} sold).`
    await searchBooks()
    await fetchSales()
  } catch (e) {
    if (e instanceof ApiError) error.value = e.message
    else error.value = String(e)
  } finally {
    submitting.value = false
  }
}

function clearSaleFilters(): void {
  saleBookFilter.value = ''
  saleMemberFilter.value = ''
  saleDateFilter.value = ''
}

onMounted(() => {
  fetchSales()
})
</script>

<template>
  <PageHeader page="Sales" :booksearch="false" />

  <main class="page">
    <section class="card">
      <h2>Optional Member Lookup</h2>

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
      <h2>Book Lookup</h2>

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
              <th>Genre</th>
              <th>ISBN</th>
              <th>On-Hand</th>
              <th>Unit Price</th>
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
              <td>{{ b.unit_price ?? '—' }}</td>
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
      <h2>Record Sale</h2>

      <form class="sale-form" @submit="submitSale">
        <div class="selection-summary">
          <div>
            <strong>Selected Book:</strong>
            <span v-if="selectedBook">
              {{ selectedBook.title }} — On-Hand:
              {{ selectedBook.inventory?.on_hand ?? 0 }}
            </span>
            <span v-else>None selected</span>
            <button type="button" @click="clearSelectedBook">Clear Book</button>
          </div>

          <div>
            <strong>Selected Member:</strong>
            <span v-if="selectedMember">
              {{ selectedMember.name }} ({{ selectedMember.email }})
            </span>
            <span v-else>Walk-in / no member selected</span>
            <button type="button" @click="clearSelectedMember">Clear Member</button>
          </div>
        </div>

        <div class="form-grid">
          <label>
            Quantity
            <input v-model="quantity" type="number" min="1" required />
          </label>

          <label>
            Unit Price
            <input v-model="unitPrice" type="number" min="0" step="0.01" required />
          </label>
        </div>

        <button type="submit" :disabled="submitting">
          {{ submitting ? 'Recording…' : 'Record Sale' }}
        </button>
      </form>
    </section>

    <section class="card">
      <h2>Recent Sales</h2>

      <div class="toolbar">
        <input v-model="saleBookFilter" type="text" placeholder="Filter by book or ISBN" />
        <input v-model="saleMemberFilter" type="text" placeholder="Filter by member" />
        <input v-model="saleDateFilter" type="text" placeholder="Sold date (YYYY-MM-DD)" />
        <button type="button" @click="clearSaleFilters">Clear Filters</button>
      </div>

      <p v-if="loadingSales">Loading sales…</p>

      <div class="table-wrap" v-else>
        <table>
          <thead>
            <tr>
              <th>Book</th>
              <th>ISBN</th>
              <th>Member</th>
              <th>Quantity</th>
              <th>Unit Price</th>
              <th>Sold At</th>
            </tr>
          </thead>

          <tbody>
            <tr v-for="sale in filteredSales" :key="sale.id">
              <td>{{ sale.book.title }}</td>
              <td>{{ sale.book.isbn }}</td>
              <td>
                <span v-if="sale.member">{{ sale.member.name }}</span>
                <span v-else>Walk-in guest</span>
              </td>
              <td>{{ sale.quantity }}</td>
              <td>{{ sale.unit_price }}</td>
              <td>{{ sale.sold_at }}</td>
            </tr>

            <tr v-if="filteredSales.length === 0">
              <td colspan="6" class="empty">No sales found</td>
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

.sale-form {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.selection-summary {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.selection-summary > div {
  display: flex;
  gap: 10px;
  align-items: center;
  flex-wrap: wrap;
}

.form-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 12px;
}

.form-grid label {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.toolbar {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  margin-bottom: 12px;
}

.toolbar input,
.form-grid input {
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
  min-width: 1000px;
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
  max-width: 150px;
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

@media (min-width: 800px) {
  .form-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>
