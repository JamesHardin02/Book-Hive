<script setup lang="ts">
import { computed, ref } from 'vue'
import PageHeader from '@/components/PageHeader.vue'
import { apiFetch, ApiError } from '@/lib/api'
import { SUBJECT_OPTIONS } from '@/lib/subjects'

type BookLookupOut = {
  isbn: string
  title: string | null
  authors: string[]
  publish_year: number | null
  cover_url: string | null
}

type LocationCreate = {
  aisle: string
  shelf: string
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
}

const lookupLoading = ref(false)
const submitting = ref(false)

const lookupError = ref<string | null>(null)
const submitError = ref<string | null>(null)
const successMessage = ref<string | null>(null)

// Form fields
const isbn = ref('')
const title = ref('')
const author = ref('')
const subject = ref('')
const year = ref('')
const edition = ref('')
const allowNewEdition = ref(false)
const unitPrice = ref('')
const coverUrl = ref('')
const initialOnHand = ref('0')
const aisle = ref('')
const shelf = ref('')
const minThreshold = ref('')

// Keeps the latest lookup result around if you want to inspect it later
const lookupResult = ref<BookLookupOut | null>(null)

function normalizeIsbn(value: string): string {
  return value.replace(/[^0-9]/g, '')
}

function toIntOrNull(v: unknown): number | null {
  const t = String(v ?? '').trim()
  if (t === '') return null
  const n = Number(t)
  return Number.isFinite(n) ? Math.trunc(n) : null
}

function toNumberOrNull(v: unknown): number | null {
  const t = String(v ?? '').trim()
  if (t === '') return null
  const n = Number(t)
  return Number.isFinite(n) ? n : null
}

const normalizedIsbn = computed(() => normalizeIsbn(isbn.value))

function clearMessages(): void {
  lookupError.value = null
  submitError.value = null
  successMessage.value = null
}

function resetForm(): void {
  isbn.value = ''
  title.value = ''
  author.value = ''
  subject.value = ''
  year.value = ''
  edition.value = ''
  allowNewEdition.value = false
  unitPrice.value = ''
  coverUrl.value = ''
  initialOnHand.value = '0'
  aisle.value = ''
  shelf.value = ''
  minThreshold.value = ''
  lookupResult.value = null
  clearMessages()
}

async function lookupIsbn(): Promise<void> {
  clearMessages()
  lookupLoading.value = true

  try {
    const digits = normalizedIsbn.value
    if (digits.length !== 10 && digits.length !== 13) {
      lookupError.value = 'ISBN must be 10 or 13 digits.'
      return
    }

    const data = await apiFetch<BookLookupOut>(`/books/lookup?isbn=${encodeURIComponent(digits)}`)
    lookupResult.value = data

    // Prefill core metadata from OpenLibrary
    isbn.value = data.isbn || digits
    title.value = data.title ?? ''
    author.value = data.authors.join(', ')
    year.value = data.publish_year != null ? String(data.publish_year) : ''
    coverUrl.value = data.cover_url ?? ''
  } catch (e) {
    if (e instanceof ApiError) lookupError.value = e.message
    else lookupError.value = String(e)
  } finally {
    lookupLoading.value = false
  }
}

function validateForm(): string | null {
  const digits = normalizedIsbn.value
  if (digits.length !== 10 && digits.length !== 13) {
    return 'ISBN must be 10 or 13 digits.'
  }

  if (!title.value.trim()) return 'Title is required.'
  if (!author.value.trim()) return 'Author is required.'
  if (!subject.value.trim()) return 'Subject is required.'

  const parsedYear = toIntOrNull(year.value)
  if (parsedYear === null || parsedYear < 0 || parsedYear > 3000) {
    return 'Year must be a valid number between 0 and 3000.'
  }

  const parsedEdition = toIntOrNull(edition.value)
  if (parsedEdition !== null && parsedEdition < 1) {
    return 'Edition must be at least 1.'
  }

  const parsedOnHand = toIntOrNull(initialOnHand.value)
  if (parsedOnHand === null || parsedOnHand < 0) {
    return 'Initial on-hand quantity must be 0 or greater.'
  }

  const parsedMinThreshold = toIntOrNull(minThreshold.value)
  if (parsedMinThreshold !== null && parsedMinThreshold < 0) {
    return 'Min threshold must be 0 or greater.'
  }

  const parsedPrice = toNumberOrNull(unitPrice.value)
  if (parsedPrice !== null && parsedPrice < 0) {
    return 'Unit price must be 0 or greater.'
  }

  const hasAisle = aisle.value.trim() !== ''
  const hasShelf = shelf.value.trim() !== ''
  if (hasAisle !== hasShelf) {
    return 'If you provide a location, both aisle and shelf are required.'
  }

  return null
}

async function submitForm(e: Event): Promise<void> {
  e.preventDefault()
  clearMessages()
  submitting.value = true

  try {
    const validationError = validateForm()
    if (validationError) {
      submitError.value = validationError
      return
    }

    const parsedYear = toIntOrNull(year.value)!
    const parsedEdition = toIntOrNull(edition.value)
    const parsedOnHand = toIntOrNull(initialOnHand.value) ?? 0
    const parsedMinThreshold = toIntOrNull(minThreshold.value)
    const parsedPrice = toNumberOrNull(unitPrice.value)

    const location: LocationCreate | null =
      aisle.value.trim() && shelf.value.trim()
        ? {
            aisle: aisle.value.trim(),
            shelf: shelf.value.trim(),
          }
        : null

    const created = await apiFetch<BookOut>('/books', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        isbn: normalizedIsbn.value,
        title: title.value.trim(),
        author: author.value.trim(),
        genre: subject.value.trim(), // UI says subject; backend field is genre
        year: parsedYear,
        unit_price: parsedPrice,
        cover_url: coverUrl.value.trim() || null,
        initial_on_hand: parsedOnHand,
        location,
        allow_new_edition: allowNewEdition.value,
        edition: parsedEdition,
      }),
    })

    if (parsedMinThreshold !== null) {
      await apiFetch(`/books/${created.id}/min-threshold`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          min_threshold: parsedMinThreshold,
        }),
      })
    }

    successMessage.value = `Created "${created.title}" successfully (ID ${created.id}, edition ${created.edition}).`
    resetForm()
    successMessage.value = `Created "${created.title}" successfully (ID ${created.id}, edition ${created.edition}).`
  } catch (e) {
    if (e instanceof ApiError) submitError.value = e.message
    else submitError.value = String(e)
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <PageHeader page="Add Book" />

  <main style="padding: 24px">
    <form class="book-form" @submit="submitForm">
      <section class="card">
        <h2>Lookup by ISBN</h2>

        <div class="lookup-row">
          <input v-model="isbn" type="text" placeholder="ISBN-10 or ISBN-13" autocomplete="off" />
          <button type="button" @click="lookupIsbn" :disabled="lookupLoading || submitting">
            {{ lookupLoading ? 'Looking up…' : 'Lookup ISBN' }}
          </button>
        </div>

        <p class="hint">
          OpenLibrary can prefill title, author, year, and cover image. Subject is still chosen
          manually.
        </p>

        <p v-if="lookupError" class="error">{{ lookupError }}</p>
      </section>

      <section class="grid">
        <section class="card">
          <h2>Book Details</h2>

          <label>
            Title
            <input v-model="title" type="text" required />
          </label>

          <label>
            Author
            <input v-model="author" type="text" required />
          </label>

          <label>
            Subject
            <select v-model="subject" required>
              <option value="">Select a subject</option>
              <option v-for="s in SUBJECT_OPTIONS" :key="s" :value="s">
                {{ s }}
              </option>
            </select>
          </label>

          <label>
            Year
            <input v-model="year" type="number" min="0" max="3000" required />
          </label>

          <label>
            Edition
            <input v-model="edition" type="number" min="1" placeholder="Optional (default 1)" />
          </label>

          <label class="checkbox-row">
            <input v-model="allowNewEdition" type="checkbox" />
            <span>Allow new edition if this ISBN already exists</span>
          </label>

          <label>
            Unit Price
            <input v-model="unitPrice" type="number" min="0" step="0.01" placeholder="Optional" />
          </label>

          <label>
            Cover URL
            <input v-model="coverUrl" type="url" placeholder="Optional" />
          </label>

          <div class="cover-preview" v-if="coverUrl">
            <img :src="coverUrl" alt="Book cover preview" />
          </div>
        </section>

        <section class="card">
          <h2>Inventory & Location</h2>

          <label>
            Initial On-Hand
            <input v-model="initialOnHand" type="number" min="0" required />
          </label>

          <label>
            Aisle
            <input v-model="aisle" type="text" placeholder="Optional unless shelf is set" />
          </label>

          <label>
            Shelf
            <input v-model="shelf" type="text" placeholder="Optional unless aisle is set" />
          </label>

          <label>
            Min Threshold
            <input v-model="minThreshold" type="number" min="0" placeholder="Optional" />
          </label>
        </section>
      </section>

      <section class="card">
        <div class="actions">
          <button type="submit" :disabled="submitting || lookupLoading">
            {{ submitting ? 'Creating…' : 'Create Book' }}
          </button>
          <button type="button" @click="resetForm" :disabled="submitting || lookupLoading">
            Reset
          </button>
        </div>

        <p v-if="submitError" class="error">{{ submitError }}</p>
        <p v-if="successMessage" class="success">{{ successMessage }}</p>
      </section>
    </form>
  </main>
</template>

<style scoped>
.book-form {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 16px;
}

.card {
  border: 1px solid #8080805f;
  border-radius: 10px;
  padding: 16px;
  background: var(--color-background);
}

.lookup-row {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  align-items: center;
}

label {
  display: flex;
  flex-direction: column;
  gap: 6px;
  margin-bottom: 12px;
}

input,
select {
  width: 100%;
  min-width: 0;
  padding: 8px;
  border: 1px solid #8080805f;
  border-radius: 6px;
  box-sizing: border-box;
}

.checkbox-row {
  flex-direction: row;
  align-items: center;
  gap: 10px;
}

.checkbox-row input {
  width: auto;
}

.actions {
  display: flex;
  gap: 12px;
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

.hint {
  margin-top: 8px;
  opacity: 0.85;
}

.error {
  color: #c00;
}

.success {
  color: #0a7a2f;
}

.cover-preview {
  margin-top: 12px;
}

.cover-preview img {
  max-width: 180px;
  width: 100%;
  height: auto;
  border-radius: 8px;
  border: 1px solid #8080805f;
}

@media (min-width: 900px) {
  .grid {
    grid-template-columns: 1.2fr 0.8fr;
  }
  button {
    max-width: 150px;
  }
}
</style>
