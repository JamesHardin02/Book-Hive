<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import PageHeader from '@/components/PageHeader.vue'
import { apiFetch, ApiError } from '@/lib/api'
import { SUBJECT_OPTIONS } from '@/lib/subjects'

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

type RowForm = {
  delta: string
  reason: string
  aisle: string
  shelf: string
  minThreshold: string
}

const loading = ref(false)
const error = ref<string | null>(null)
const actionMessage = ref<string | null>(null)
const books = ref<BookOut[]>([])

const titleFilter = ref('')
const authorFilter = ref('')
const subjectFilter = ref('')
const isbnFilter = ref('')

// client-side inventory filters
const editionFilter = ref('')
const onHandFilter = ref('')
const thresholdFilter = ref('')
const locationFilter = ref('')

const offset = ref(0)
const limit = ref(25)

const rowForms = ref<Record<number, RowForm>>({})
const savingId = ref<number | null>(null)

function normalizeIsbn(s: string): string {
  return s.replace(/[^0-9]/g, '')
}

function toIntOrNull(v: unknown): number | null {
  const t = String(v ?? '').trim()
  if (t === '') return null
  const n = Number(t)
  return Number.isFinite(n) ? Math.trunc(n) : null
}

function isSaving(bookId: number): boolean {
  return savingId.value === bookId
}

function setActionMessage(message: string | null) {
  actionMessage.value = message
}

function buildListQuery(): string {
  const params = new URLSearchParams()

  if (titleFilter.value.trim()) params.set('title', titleFilter.value.trim())
  if (authorFilter.value.trim()) params.set('author', authorFilter.value.trim())
  if (subjectFilter.value.trim()) params.set('genre', subjectFilter.value.trim())
  if (isbnFilter.value.trim()) params.set('isbn', normalizeIsbn(isbnFilter.value.trim()))

  params.set('offset', String(offset.value))
  params.set('limit', String(limit.value))

  return params.toString()
}

function syncRowForms(data: BookOut[]): void {
  const next: Record<number, RowForm> = {}

  for (const b of data) {
    next[b.id] = {
      delta: '',
      reason: '',
      aisle: b.inventory?.location?.aisle ?? '',
      shelf: b.inventory?.location?.shelf ?? '',
      minThreshold:
        b.inventory?.min_threshold !== undefined && b.inventory?.min_threshold !== null
          ? String(b.inventory.min_threshold)
          : '',
    }
  }

  rowForms.value = next
}

async function fetchBooks(): Promise<void> {
  loading.value = true
  error.value = null

  try {
    const query = buildListQuery()
    const path = query ? `/books?${query}` : '/books'
    const data = await apiFetch<BookOut[]>(path)
    books.value = data
    syncRowForms(data)
  } catch (e) {
    if (e instanceof ApiError) error.value = e.message
    else error.value = String(e)
    books.value = []
    rowForms.value = {}
  } finally {
    loading.value = false
  }
}

const filteredBooks = computed(() => {
  const edition = toIntOrNull(editionFilter.value)
  const onHand = toIntOrNull(onHandFilter.value)
  const threshold = thresholdFilter.value.trim().toLowerCase()
  const location = locationFilter.value.trim().toLowerCase()

  return books.value.filter((b) => {
    if (edition !== null && b.edition !== edition) return false

    if (onHand !== null && (b.inventory?.on_hand ?? null) !== onHand) return false

    if (threshold) {
      const currentThreshold =
        b.inventory?.min_threshold === null || b.inventory?.min_threshold === undefined
          ? 'default'
          : String(b.inventory.min_threshold)

      if (!currentThreshold.toLowerCase().includes(threshold)) return false
    }

    if (location) {
      const loc = b.inventory?.location
      const display = loc ? `${loc.aisle} / ${loc.shelf}`.toLowerCase() : ''
      if (!display.includes(location)) return false
    }

    return true
  })
})

function clearFilters(): void {
  titleFilter.value = ''
  authorFilter.value = ''
  subjectFilter.value = ''
  isbnFilter.value = ''
  editionFilter.value = ''
  onHandFilter.value = ''
  thresholdFilter.value = ''
  locationFilter.value = ''
  offset.value = 0
  fetchBooks()
}

function onSearch(e: Event): void {
  e.preventDefault()
  offset.value = 0
  fetchBooks()
}

function nextPage(): void {
  offset.value += limit.value
  fetchBooks()
}

function prevPage(): void {
  offset.value = Math.max(0, offset.value - limit.value)
  fetchBooks()
}

async function applyStock(book: BookOut): Promise<void> {
  const form = rowForms.value[book.id]
  if (!form) return

  const delta = toIntOrNull(form.delta)
  const reason = form.reason.trim()

  if (delta === null || delta === 0) {
    error.value = `Enter a non-zero stock adjustment for "${book.title}".`
    return
  }

  if (!reason) {
    error.value = `Reason is required for stock adjustment on "${book.title}".`
    return
  }

  savingId.value = book.id
  error.value = null
  setActionMessage(null)

  try {
    await apiFetch(`/books/${book.id}/stock`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        delta,
        reason,
      }),
    })

    setActionMessage(`Stock updated for "${book.title}".`)
    await fetchBooks()
  } catch (e) {
    if (e instanceof ApiError) error.value = e.message
    else error.value = String(e)
  } finally {
    savingId.value = null
  }
}

async function saveLocation(book: BookOut): Promise<void> {
  const form = rowForms.value[book.id]
  if (!form) return

  const aisle = form.aisle.trim()
  const shelf = form.shelf.trim()

  if (!aisle || !shelf) {
    error.value = `Both aisle and shelf are required to update location for "${book.title}".`
    return
  }

  savingId.value = book.id
  error.value = null
  setActionMessage(null)

  try {
    const path = `/books/${book.id}/location?aisle=${encodeURIComponent(aisle)}&shelf=${encodeURIComponent(shelf)}`
    await apiFetch(path, {
      method: 'PATCH',
    })

    setActionMessage(`Location updated for "${book.title}".`)
    await fetchBooks()
  } catch (e) {
    if (e instanceof ApiError) error.value = e.message
    else error.value = String(e)
  } finally {
    savingId.value = null
  }
}

async function saveThreshold(book: BookOut): Promise<void> {
  const form = rowForms.value[book.id]
  if (!form) return

  const minThreshold = toIntOrNull(form.minThreshold)

  savingId.value = book.id
  error.value = null
  setActionMessage(null)

  try {
    await apiFetch(`/books/${book.id}/min-threshold`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        min_threshold: minThreshold,
      }),
    })

    setActionMessage(`Threshold updated for "${book.title}".`)
    await fetchBooks()
  } catch (e) {
    if (e instanceof ApiError) error.value = e.message
    else error.value = String(e)
  } finally {
    savingId.value = null
  }
}

function getRowForm(bookId: number): RowForm {
  if (!rowForms.value[bookId]) {
    rowForms.value[bookId] = {
      delta: '',
      reason: '',
      aisle: '',
      shelf: '',
      minThreshold: '',
    }
  }

  return rowForms.value[bookId]
}

function clearThresholdInput(bookId: number): void {
  getRowForm(bookId).minThreshold = ''
}

onMounted(() => {
  fetchBooks()
})
</script>

<template>
  <PageHeader page="Inventory" />

  <main style="padding: 24px">
    <form class="toolbar" @submit="onSearch">
      <div class="submission">
        <button type="submit" :disabled="loading">Search</button>
        <button type="button" @click="clearFilters" :disabled="loading">Clear</button>
      </div>

      <div class="pager">
        <button type="button" @click="prevPage" :disabled="loading || offset === 0">Prev</button>
        <button type="button" @click="nextPage" :disabled="loading">Next</button>
      </div>
    </form>

    <p v-if="loading">Loading inventory…</p>
    <p v-else-if="error" class="error">{{ error }}</p>
    <p v-if="actionMessage" class="success">{{ actionMessage }}</p>

    <div class="table-wrap" v-if="!loading">
      <table>
        <thead>
          <tr>
            <th><input v-model="titleFilter" type="text" placeholder="Title" /></th>
            <th><input v-model="authorFilter" type="text" placeholder="Author" /></th>

            <th>
              <select v-model="subjectFilter">
                <option value="">All subjects</option>
                <option v-for="s in SUBJECT_OPTIONS" :key="s" :value="s">{{ s }}</option>
              </select>
            </th>

            <th><input v-model="isbnFilter" type="text" placeholder="ISBN" /></th>
            <th><input v-model="editionFilter" type="number" min="1" placeholder="Edition" /></th>
            <th><input v-model="onHandFilter" type="number" min="0" placeholder="On-Hand" /></th>
            <th><input v-model="thresholdFilter" type="text" placeholder="Threshold / default" /></th>
            <th><input v-model="locationFilter" type="text" placeholder="Aisle / Shelf" /></th>
            <th>—</th>
            <th>—</th>
            <th>—</th>
          </tr>

          <tr>
            <th>Title</th>
            <th>Author</th>
            <th>Subject</th>
            <th>ISBN</th>
            <th>Edition</th>
            <th>On-Hand</th>
            <th>Threshold</th>
            <th>Location</th>
            <th>Stock Adjustment</th>
            <th>Update Location</th>
            <th>Update Threshold</th>
          </tr>
        </thead>

        <tbody>
          <tr v-for="b in filteredBooks" :key="b.id">
            <td class="truncate" :title="b.title">{{ b.title }}</td>
            <td class="truncate" :title="b.author">{{ b.author }}</td>
            <td>{{ b.genre }}</td>
            <td class="truncate" :title="b.isbn">{{ b.isbn }}</td>
            <td>{{ b.edition }}</td>
            <td>{{ b.inventory?.on_hand ?? '—' }}</td>
            <td>{{ b.inventory?.min_threshold ?? 'default' }}</td>

            <td>
              <span v-if="b.inventory?.location">
                {{ b.inventory.location.aisle }} / {{ b.inventory.location.shelf }}
              </span>
              <span v-else>—</span>
            </td>

            <td>
              <div class="cell-form">
                <input
                  v-model="getRowForm(b.id).delta"
                  type="number"
                  placeholder="+/- qty"
                  :disabled="isSaving(b.id)"
                />
                <input
                  v-model="getRowForm(b.id).reason"
                  type="text"
                  placeholder="Reason"
                  :disabled="isSaving(b.id)"
                />
                <button type="button" @click="applyStock(b)" :disabled="isSaving(b.id)">
                  {{ isSaving(b.id) ? 'Saving…' : 'Apply' }}
                </button>
              </div>
            </td>

            <td>
              <div class="cell-form">
                <input
                  v-model="getRowForm(b.id).aisle"
                  type="text"
                  placeholder="Aisle"
                  :disabled="isSaving(b.id)"
                />
                <input
                  v-model="getRowForm(b.id).shelf"
                  type="text"
                  placeholder="Shelf"
                  :disabled="isSaving(b.id)"
                />
                <button type="button" @click="saveLocation(b)" :disabled="isSaving(b.id)">
                  {{ isSaving(b.id) ? 'Saving…' : 'Save' }}
                </button>
              </div>
            </td>

            <td>
              <div class="cell-form">
                <input
                  v-model="getRowForm(b.id).minThreshold"
                  type="number"
                  min="0"
                  placeholder="Min threshold"
                  :disabled="isSaving(b.id)"
                />
                <div class="button-row">
                  <button type="button" @click="saveThreshold(b)" :disabled="isSaving(b.id)">
                    {{ isSaving(b.id) ? 'Saving…' : 'Save' }}
                  </button>
                  <button
                    type="button"
                    @click="clearThresholdInput(b.id)"
                    :disabled="isSaving(b.id)"
                  >
                    Clear
                  </button>
                </div>
              </div>
            </td>
          </tr>

          <tr v-if="!error && filteredBooks.length === 0">
            <td colspan="11" style="text-align: center; padding: 16px">No inventory records found</td>
          </tr>
        </tbody>
      </table>
    </div>
  </main>
</template>

<style scoped>
.toolbar {
  display: flex;
  gap: 12px;
  align-items: center;
  margin-bottom: 16px;
  flex-wrap: wrap;
}

.submission {
  display: flex;
  gap: 8px;
}

.pager {
  margin-left: auto;
  display: flex;
  gap: 8px;
  align-items: center;
}

.table-wrap {
  width: 100%;
  overflow-x: auto;
  -webkit-overflow-scrolling: touch;
}

table {
  min-width: 1500px;
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

thead input,
thead select {
  width: 100%;
  min-width: 0;
  padding: 8px;
  border: 1px solid #8080805f;
  border-radius: 6px;
  box-sizing: border-box;
}

.truncate {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.cell-form {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.cell-form input {
  width: 100%;
  min-width: 0;
  padding: 8px;
  border: 1px solid #8080805f;
  border-radius: 6px;
  box-sizing: border-box;
}

.button-row {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
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
</style>