<script setup lang="ts">
import { ref } from 'vue'
import PageHeader from '@/components/PageHeader.vue'

const loadingKey = ref<string | null>(null)
const error = ref<string | null>(null)
const successMessage = ref<string | null>(null)

const activeLoansOnly = ref(true)

function getApiBase(): string {
  return import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'
}

async function downloadCsv(path: string, filename: string, key: string): Promise<void> {
  loadingKey.value = key
  error.value = null
  successMessage.value = null

  try {
    const res = await fetch(`${getApiBase()}${path}`, {
      method: 'GET',
      credentials: 'include',
    })

    if (!res.ok) {
      let message = `${res.status} ${res.statusText}`
      try {
        const data = await res.json()
        if (typeof data?.detail === 'string') message = data.detail
      } catch {
        // leave fallback message
      }
      throw new Error(message)
    }

    const blob = await res.blob()
    const url = window.URL.createObjectURL(blob)

    const a = document.createElement('a')
    a.href = url
    a.download = filename
    document.body.appendChild(a)
    a.click()
    a.remove()

    window.URL.revokeObjectURL(url)
    successMessage.value = `Downloaded ${filename}`
  } catch (e) {
    error.value = e instanceof Error ? e.message : String(e)
  } finally {
    loadingKey.value = null
  }
}

function exportBooks(): void {
  void downloadCsv('/exports/books.csv', 'books.csv', 'books')
}

function exportMembers(): void {
  void downloadCsv('/exports/members.csv', 'members.csv', 'members')
}

function exportLoans(): void {
  const path = activeLoansOnly.value ? '/exports/loans.csv?active_only=true' : '/exports/loans.csv'
  const filename = activeLoansOnly.value ? 'loans_active.csv' : 'loans.csv'
  void downloadCsv(path, filename, 'loans')
}

function exportSales(): void {
  void downloadCsv('/exports/sales.csv', 'sales.csv', 'sales')
}
</script>

<template>
  <PageHeader page="Exports" />
  <p v-if="error" class="error">{{ error }}</p>
  <p v-if="successMessage" class="success">{{ successMessage }}</p>

  <main class="page">
    <section class="card">
      <h2>Books Export</h2>
      <p>
        Download all books with inventory, threshold, and location columns for spreadsheet review.
      </p>
      <button type="button" @click="exportBooks" :disabled="loadingKey === 'books'">
        {{ loadingKey === 'books' ? 'Downloading…' : 'Download Books CSV' }}
      </button>
    </section>

    <section class="card">
      <h2>Members Export</h2>
      <p>Download all registered members with contact information.</p>
      <button
        id="members-btn"
        type="button"
        @click="exportMembers"
        :disabled="loadingKey === 'members'"
      >
        {{ loadingKey === 'members' ? 'Downloading…' : 'Download Members CSV' }}
      </button>
    </section>

    <section class="card">
      <h2>Loans Export</h2>
      <p>
        Download circulation records for reporting and audit review.
      </p>

      <label class="checkbox">
        <input v-model="activeLoansOnly" type="checkbox" />
        Export active loans only
      </label>

      <button type="button" @click="exportLoans" :disabled="loadingKey === 'loans'">
        {{ loadingKey === 'loans' ? 'Downloading…' : 'Download Loans CSV' }}
      </button>
    </section>

    <section class="card">
      <h2>Sales Export</h2>
      <p>Download manual sales records including quantity, unit price, and line totals.</p>
      <button id="sales-btn" type="button" @click="exportSales" :disabled="loadingKey === 'sales'">
        {{ loadingKey === 'sales' ? 'Downloading…' : 'Download Sales CSV' }}
      </button>
    </section>
  </main>
</template>

<style scoped>
.page {
  padding: 24px;
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

.card h2 {
  margin-bottom: 8px;
}

.card p {
  margin-bottom: 12px;
}

.checkbox {
  display: flex;
  gap: 8px;
  align-items: center;
  margin-bottom: 12px;
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
  padding: 0 24px;
}

.success {
  color: #0a7a2f;
  padding: 0 24px;
}

@media (min-width: 900px) {
  .page {
    grid-template-columns: 1fr 1fr;
  }

  #sales-btn {
    margin-top: 35px;
  }
}

@media (min-width: 995px) {
  #sales-btn {
    margin-top: 12px;
  }
}

@media (min-width: 983px) {
  #members-btn {
    margin-top: 23px;
  }
}

@media (min-width: 1210px) {
  #sales-btn {
    margin-top: 35px;
  }
}
</style>

