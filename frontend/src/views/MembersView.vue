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

type EditForm = {
  name: string
  email: string
  phone_number: string
}

const loading = ref(false)
const saving = ref(false)
const deletingId = ref<number | null>(null)

const error = ref<string | null>(null)
const successMessage = ref<string | null>(null)

const members = ref<MemberOut[]>([])
const editForms = ref<Record<number, EditForm>>({})

// create form
const createName = ref('')
const createEmail = ref('')
const createPhoneNumber = ref('')

// filters
const nameFilter = ref('')
const emailFilter = ref('')
const phoneFilter = ref('')

// paging
const offset = ref(0)
const limit = ref(25)

function getEditForm(member: MemberOut): EditForm {
  let form = editForms.value[member.id]

  if (!form) {
    form = {
      name: member.name,
      email: member.email,
      phone_number: member.phone_number,
    }
    editForms.value[member.id] = form
  }

  return form
}

function clearMessages(): void {
  error.value = null
  successMessage.value = null
}

function buildQuery(): string {
  const params = new URLSearchParams()

  if (nameFilter.value.trim()) params.set('name', nameFilter.value.trim())
  if (emailFilter.value.trim()) params.set('email', emailFilter.value.trim())
  if (phoneFilter.value.trim()) params.set('phone_number', phoneFilter.value.trim())

  params.set('offset', String(offset.value))
  params.set('limit', String(limit.value))
  return params.toString()
}

async function fetchMembers(): Promise<void> {
  loading.value = true
  error.value = null

  try {
    const query = buildQuery()
    const path = query ? `/members?${query}` : '/members'
    const data = await apiFetch<MemberOut[]>(path)
    members.value = data

    const nextForms: Record<number, EditForm> = {}
    for (const m of data) {
      nextForms[m.id] = {
        name: m.name,
        email: m.email,
        phone_number: m.phone_number,
      }
    }
    editForms.value = nextForms
  } catch (e) {
    if (e instanceof ApiError) error.value = e.message
    else error.value = String(e)
    members.value = []
    editForms.value = {}
  } finally {
    loading.value = false
  }
}

function clearFilters(): void {
  nameFilter.value = ''
  emailFilter.value = ''
  phoneFilter.value = ''
  offset.value = 0
  fetchMembers()
}

function onSearch(e: Event): void {
  e.preventDefault()
  offset.value = 0
  fetchMembers()
}

function nextPage(): void {
  offset.value += limit.value
  fetchMembers()
}

function prevPage(): void {
  offset.value = Math.max(0, offset.value - limit.value)
  fetchMembers()
}

function resetCreateForm(): void {
  createName.value = ''
  createEmail.value = ''
  createPhoneNumber.value = ''
}

async function createMember(e: Event): Promise<void> {
  e.preventDefault()
  clearMessages()
  saving.value = true

  try {
    const created = await apiFetch<MemberOut>('/members', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        name: createName.value.trim(),
        email: createEmail.value.trim(),
        phone_number: createPhoneNumber.value.trim(),
      }),
    })

    successMessage.value = `Created member "${created.name}".`
    resetCreateForm()
    await fetchMembers()
  } catch (e) {
    if (e instanceof ApiError) error.value = e.message
    else error.value = String(e)
  } finally {
    saving.value = false
  }
}

async function saveMember(member: MemberOut): Promise<void> {
  clearMessages()
  saving.value = true

  try {
    const form = getEditForm(member)

    const updated = await apiFetch<MemberOut>(`/members/${member.id}`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        name: form.name.trim(),
        email: form.email.trim(),
        phone_number: form.phone_number.trim(),
      }),
    })

    successMessage.value = `Updated member "${updated.name}".`
    await fetchMembers()
  } catch (e) {
    if (e instanceof ApiError) error.value = e.message
    else error.value = String(e)
  } finally {
    saving.value = false
  }
}

async function deleteMember(member: MemberOut): Promise<void> {
  clearMessages()
  deletingId.value = member.id

  try {
    await apiFetch(`/members/${member.id}`, {
      method: 'DELETE',
    })

    successMessage.value = `Deleted member "${member.name}".`
    await fetchMembers()
  } catch (e) {
    if (e instanceof ApiError) error.value = e.message
    else error.value = String(e)
  } finally {
    deletingId.value = null
  }
}

const filteredMembers = computed(() => members.value)

onMounted(() => {
  fetchMembers()
})
</script>

<template>
  <PageHeader page="Members" />

  <main style="padding: 24px">
    <section class="card">
      <h2>Register Member</h2>

      <form class="create-form" @submit="createMember">
        <label>
          Name
          <input v-model="createName" type="text" required />
        </label>

        <label>
          Email
          <input v-model="createEmail" type="email" required />
        </label>

        <label>
          Phone Number
          <input v-model="createPhoneNumber" type="text" required />
        </label>

        <div class="actions">
          <button type="submit" :disabled="saving">
            {{ saving ? 'Creating…' : 'Create Member' }}
          </button>
          <button type="button" @click="resetCreateForm" :disabled="saving">Reset</button>
        </div>
      </form>
    </section>

    <section class="card">
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

      <p v-if="loading">Loading members…</p>
      <p v-else-if="error" class="error">{{ error }}</p>
      <p v-if="successMessage" class="success">{{ successMessage }}</p>

      <div class="table-wrap" v-if="!loading">
        <table>
          <thead>
            <tr>
              <th><input v-model="nameFilter" type="text" placeholder="Name" /></th>
              <th><input v-model="emailFilter" type="text" placeholder="Email" /></th>
              <th><input v-model="phoneFilter" type="text" placeholder="Phone" /></th>
              <th>—</th>
              <th>—</th>
            </tr>

            <tr>
              <th>Name</th>
              <th>Email</th>
              <th>Phone Number</th>
              <th>Created</th>
              <th>Actions</th>
            </tr>
          </thead>

          <tbody>
            <tr v-for="m in filteredMembers" :key="m.id">
              <td>
                <input v-model="getEditForm(m).name" type="text" />
              </td>

              <td>
                <input v-model="getEditForm(m).email" type="email" />
              </td>

              <td>
                <input v-model="getEditForm(m).phone_number" type="text" />
              </td>

              <td>{{ m.created_at }}</td>

              <td>
                <div class="button-row">
                  <button type="button" @click="saveMember(m)" :disabled="saving">
                    {{ saving ? 'Saving…' : 'Save' }}
                  </button>
                  <button type="button" @click="deleteMember(m)" :disabled="deletingId === m.id">
                    {{ deletingId === m.id ? 'Deleting…' : 'Delete' }}
                  </button>
                </div>
              </td>
            </tr>

            <tr v-if="!error && filteredMembers.length === 0">
              <td colspan="5" style="text-align: center; padding: 16px">No members found</td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>
  </main>
</template>

<style scoped>
main {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.submission {
  display: flex;
  gap: 8px;
}

.card {
  border: 1px solid #8080805f;
  border-radius: 10px;
  padding: 16px;
  background: var(--color-background);
}

.create-form {
  display: grid;
  grid-template-columns: 1fr;
  gap: 12px;
}

label {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

input {
  width: 100%;
  min-width: 0;
  padding: 8px;
  border: 1px solid #8080805f;
  border-radius: 6px;
  box-sizing: border-box;
}

.toolbar {
  display: flex;
  gap: 12px;
  align-items: center;
  margin-bottom: 16px;
  flex-wrap: wrap;
}

.pager {
  margin-left: auto;
  display: flex;
  gap: 8px;
  align-items: center;
}

.actions,
.button-row {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
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
  table-layout: fixed;
}

th,
td {
  border: 1px solid #8080805f;
  padding: 8px;
  text-align: left;
  vertical-align: top;
}

thead input {
  width: 100%;
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

@media (min-width: 900px) {
  .create-form {
    grid-template-columns: repeat(3, 1fr);
    align-items: end;
  }

  .actions {
    flex-wrap: nowrap;
  }
}
</style>
