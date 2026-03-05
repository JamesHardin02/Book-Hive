<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import PageHeader from '@/components/PageHeader.vue'
import { apiFetch, ApiError } from '@/lib/api'

type LocationOut = { id: number; aisle: string; shelf: string }
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

const loading = ref(false)
const error = ref<string | null>(null)
const books = ref<BookOut[]>([])

// Filters (1 input per column)
const title = ref('')
const author = ref('')
const genre = ref('')
const year = ref<string>('') // single Year filter -> mapped to year_min/year_max
const edition = ref('')
const isbn = ref('')
const onHand = ref('')
const aisle = ref('')
const shelf = ref('')
const created = ref('')

// Paging
const offset = ref(0)
const limit = ref(25)

function normalizeIsbn(s: string): string {
  return s.replace(/[^0-9]/g, '')
}

function toIntOrNull(v: unknown): number | null {
  const t = String(v ?? '').trim()
  if (t === '') return null
  const n = Number(t)
  return Number.isFinite(n) ? Math.trunc(n) : null
}

function buildQuery(): string {
  const params = new URLSearchParams()

  if (title.value.trim()) params.set('title', title.value.trim())
  if (author.value.trim()) params.set('author', author.value.trim())
  if (genre.value.trim()) params.set('genre', genre.value.trim())
  if (isbn.value.trim()) params.set('isbn', normalizeIsbn(isbn.value.trim()))

  // single Year box, but backend uses year_min/year_max.
  const y = toIntOrNull(year.value)
  if (y !== null) {
    params.set('year_min', String(y))
    params.set('year_max', String(y))
  }

  params.set('offset', String(offset.value))
  params.set('limit', String(limit.value))
  return params.toString()
}

async function fetchBooks(): Promise<void> {
  loading.value = true
  error.value = null

  try {
    const query = buildQuery()
    const path = query ? `/books?${query}` : '/books'
    books.value = await apiFetch<BookOut[]>(path)
  } catch (e) {
    if (e instanceof ApiError) error.value = e.message
    else error.value = String(e)
    books.value = []
  } finally {
    loading.value = false
  }
}

function clearFilters(): void {
  title.value = ''
  author.value = ''
  genre.value = ''
  year.value = ''
  edition.value = ''
  isbn.value = ''
  onHand.value = ''
  aisle.value = ''
  shelf.value = ''
  created.value = ''
  offset.value = 0
  fetchBooks()
}

// Dropdown options from currently loaded page
const genreOptions = computed(() => {
  const set = new Set<string>()
  for (const b of books.value) {
    if (b.genre) set.add(b.genre)
  }
  return Array.from(set).sort((a, b) => a.localeCompare(b))
})

const filteredBooks = computed(() => {
  const ed = toIntOrNull(edition.value)
  const a = aisle.value.trim().toLowerCase()
  const s = shelf.value.trim().toLowerCase()
  const oh = toIntOrNull(onHand.value)
  const cr = created.value.trim()

  return books.value.filter((b) => {
    // edition (client-side)
    if (ed !== null && b.edition !== ed) return false

    // on-hand (client-side exact match)
    if (oh !== null && (b.inventory?.on_hand ?? null) !== oh) return false

    // aisle/shelf (client-side contains)
    if (a || s) {
      const loc = b.inventory?.location
      if (!loc) return false
      const aisleOk = !a || String(loc.aisle).toLowerCase().includes(a)
      const shelfOk = !s || String(loc.shelf).toLowerCase().includes(s)
      if (!aisleOk || !shelfOk) return false
    }

    // created (client-side substring match; user can type YYYY-MM-DD)
    if (cr) {
      if (!String(b.created_at).includes(cr)) return false
    }

    return true
  })
})

function onSubmit(e: Event) {
  e.preventDefault()
  offset.value = 0
  fetchBooks()
}

function nextPage() {
  offset.value += limit.value
  fetchBooks()
}

function prevPage() {
  offset.value = Math.max(0, offset.value - limit.value)
  fetchBooks()
}

onMounted(() => {
  fetchBooks()
})
</script>

<template>
  <PageHeader page="Search" />

  <main style="padding: 24px">
    <form @submit="onSubmit">
      <div class="toolbar">
        <button type="submit" :disabled="loading">Search</button>
        <button type="button" @click="clearFilters" :disabled="loading">Clear</button>

        <div class="pager">
          <button type="button" @click="prevPage" :disabled="loading || offset === 0">Prev</button>
          <button type="button" @click="nextPage" :disabled="loading">Next</button>
        </div>
      </div>

      <p v-if="loading">Loading…</p>
      <p v-else-if="error" style="color: #c00">Error: {{ error }}</p>

      <table>
        <thead>
          <tr>
            <th><input v-model="title" type="text" placeholder="Title" /></th>
            <th><input v-model="author" type="text" placeholder="Author" /></th>

            <th>
              <select v-model="genre">
                <option value="">All genres</option>
                <option v-for="g in genreOptions" :key="g" :value="g">{{ g }}</option>
              </select>
            </th>

            <th><input v-model="year" type="number" placeholder="Year" min="0" max="3000" /></th>
            <th>
              <input v-model="edition" type="number" placeholder="Edition" min="1" max="3000" />
            </th>
            <th><input v-model="isbn" type="text" placeholder="ISBN" /></th>
            <th><input v-model="onHand" type="number" placeholder="On-Hand" min="0" /></th>
            <th><input v-model="aisle" type="text" placeholder="Aisle" /></th>
            <th><input v-model="shelf" type="text" placeholder="Shelf" /></th>
            <th><input v-model="created" type="text" placeholder="Created (YYYY-MM-DD)" /></th>
          </tr>

          <tr>
            <th>Title</th>
            <th>Author</th>
            <th>Genre</th>
            <th>Year</th>
            <th>Edition</th>
            <th>ISBN</th>
            <th>On-Hand</th>
            <th class="truncate">Location</th>
            <th class="truncate">Threshold</th>
            <th>Created</th>
          </tr>
        </thead>

        <tbody>
          <tr v-for="b in filteredBooks" :key="b.id">
            <td class="truncate" :title="b.title">{{ b.title }}</td>
            <td class="truncate" :title="b.author">{{ b.author }}</td>
            <td>{{ b.genre }}</td>
            <td>{{ b.year }}</td>
            <td>{{ b.edition }}</td>
            <td class="truncate" :title="b.isbn">{{ b.isbn }}</td>

            <td>{{ b.inventory?.on_hand ?? '—' }}</td>

            <td>
              <span v-if="b.inventory?.location">
                {{ b.inventory.location.aisle }} / {{ b.inventory.location.shelf }}
              </span>
              <span v-else>—</span>
            </td>

            <td>{{ b.inventory?.min_threshold ?? 'default' }}</td>
            <td>{{ b.created_at }}</td>
          </tr>

          <tr v-if="!loading && !error && filteredBooks.length === 0">
            <td colspan="10" style="text-align: center; padding: 16px">No results</td>
          </tr>
        </tbody>
      </table>
    </form>
  </main>
</template>

<style scoped>
.toolbar {
  display: flex;
  gap: 12px;
  align-items: center;
  margin-bottom: 12px;
  flex-wrap: wrap;
}

.pager {
  margin-left: auto;
  display: flex;
  gap: 8px;
  align-items: center;
}

table {
  width: 100%;
  border-collapse: collapse;
  table-layout: fixed;
}

th,
td {
  border: 1px solid #8080805f;
  padding: 6px;
  text-align: left;
  vertical-align: top;
}

th.truncate,
td.truncate {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

thead input,
thead select {
  width: 100%;
  min-width: 0;
  padding: 8px;
  border: 1px solid #8080805f;
  border-radius: 6px;
  box-sizing: border-box;
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
</style>
