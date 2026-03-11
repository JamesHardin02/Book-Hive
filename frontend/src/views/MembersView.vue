<script setup lang="ts">
import { ref, computed } from 'vue'
import PageHeader from '@/components/PageHeader.vue'

// Local-only UI: selection + inline edit; no backend calls here
type MemberRow = { id: number; name?: string; email?: string; phone_number?: string; created_at?: string }

const members = ref<MemberRow[]>([])
const search = ref('')
const placeholderCount = 7

const filtered = computed(() => {
  const q = search.value.trim().toLowerCase()
  if (!q) return members.value
  return members.value.filter((m) => (m.name || '').toLowerCase().includes(q) || (m.email || '').toLowerCase().includes(q))
})

const placeholders = computed(() => Array.from({ length: placeholderCount }))

// selection and inline edit state
const selectedId = ref<number | null>(null)
const editingId = ref<number | null>(null)
const editModel = ref<Partial<MemberRow>>({})

function onSelect(id: number, checked: boolean) {
  selectedId.value = checked ? id : null
  if (!checked) {
    editingId.value = null
    editModel.value = {}
  }
}

function startEdit() {
  if (!selectedId.value) return
  const m = members.value.find((x) => x.id === selectedId.value)
  if (!m) return
  editingId.value = m.id
  editModel.value = { ...m }
}

function saveEdit() {
  if (!editingId.value) return
  const idx = members.value.findIndex((x) => x.id === editingId.value)
  if (idx === -1) return
  members.value[idx] = { ...members.value[idx], ...(editModel.value as MemberRow) }
  editingId.value = null
  selectedId.value = null
  editModel.value = {}
}

function cancelEdit() {
  editingId.value = null
  editModel.value = {}
}

function deleteMember() {
  if (!selectedId.value) return
  const idx = members.value.findIndex((x) => x.id === selectedId.value)
  if (idx === -1) return
  if (!confirm('Delete selected member?')) return
  members.value.splice(idx, 1)
  selectedId.value = null
  editingId.value = null
}
</script>

<template>
  <PageHeader page="Members" />
  <main style="padding: 24px">
    <form>
      <section>
        <h2>Members</h2>

        <div class="header-actions">
          <button class="primary">+ Add Member</button>
          <div class="action-controls">
            <button v-if="selectedId && !editingId" @click="startEdit">Edit Member</button>
            <button v-if="selectedId && !editingId" @click="deleteMember">Delete Member</button>
            <button v-if="editingId" @click="saveEdit">Save</button>
            <button v-if="editingId" @click="cancelEdit">Cancel</button>
          </div>
          <div class="search-wrap">
            <input id="member-search" v-model="search" type="text" placeholder="Type member name..." aria-label="Search member" />
          </div>
        </div>

        <div class="members-table-wrap">
          <table class="members-table">
            <thead>
              <tr>
                <th style="width:40px"></th>
                <th>ID</th>
                <th>Name</th>
                <th>Email</th>
                <th>Phone</th>
                <th>Joined</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="m in filtered" :key="m.id">
                <td>
                  <input
                    type="checkbox"
                    :checked="selectedId === m.id"
                    @change="(e) => onSelect(m.id, (e.target as HTMLInputElement).checked)"
                  />
                </td>
                <td>{{ m.id }}</td>
                <td v-if="editingId !== m.id">{{ m.name }}</td>
                <td v-else><input v-model="editModel.name" /></td>
                <td v-if="editingId !== m.id">{{ m.email }}</td>
                <td v-else><input v-model="editModel.email" /></td>
                <td v-if="editingId !== m.id">{{ m.phone_number }}</td>
                <td v-else><input v-model="editModel.phone_number" /></td>
                <td v-if="editingId !== m.id">{{ m.created_at }}</td>
                <td v-else><input v-model="editModel.created_at" /></td>
              </tr>
              <tr v-if="filtered.length === 0" class="placeholder-row" v-for="(_, i) in placeholders" :key="`ph-${i}`">
                <td class="placeholder">
                  <input
                    type="checkbox"
                    :checked="selectedId === -(i + 1)"
                    @change="(e) => onSelect(-(i + 1), (e.target as HTMLInputElement).checked)"
                  />
                </td>
                <td class="placeholder">—</td>
                <td class="placeholder">&nbsp;</td>
                <td class="placeholder">&nbsp;</td>
                <td class="placeholder">&nbsp;</td>
                <td class="placeholder">&nbsp;</td>
              </tr>
            </tbody>
          </table>
        </div>

      </section>
    </form>
  </main>
</template>

<style scoped>
form {
  margin: 40px auto;
  padding: 24px;
  background: var(--color-background-soft);
  border: 1px solid var(--color-border);
  border-radius: 8px;
  gap: 32px;
}

section {
  padding: 20px;
  background: var(--color-background);
  border: 1px solid var(--color-border);
  border-radius: 6px;
}

h2 {
  margin-bottom: 12px;
  margin-right: 12px;
  color: var(--color-heading);
}

.section-header {
  display: flex;
  align-items: center;
  gap: 12px;
}

.section-header h2 {
  margin: 0;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}

.header-actions .search-wrap {
  display: flex;
  align-items: center;
}

.header-actions input[type="text"] {
  width: 320px;
  padding: 8px 10px;
  margin: 0;
}

.members-table-wrap {
  margin-top: 12px;
}

.members-table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 8px;
}

.members-table th,
.members-table td {
  border: 1px solid var(--color-border);
  padding: 8px 10px;
  text-align: left;
}

.members-table thead th {
  background: var(--color-background-soft);
}

.members-table .placeholder {
  color: var(--color-text);
  opacity: 0.55;
}

.members-table .placeholder-row td {
  background: var(--color-background-mute);
}

.action-controls button {
  width: auto;
  padding: 8px 10px;
  background: var(--vt-c-slate, #6b7280);
}
.action-controls {
  display: flex;
  gap: 8px;
  align-items: center;
}
.members-table thead th:first-child,
.members-table tbody td:first-child {
  text-align: center;
  width: 40px;
}

label {
  display: block;
  margin-bottom: 6px;
  font-size: 14px;
  color: var(--color-text);
}

input,
select {
  width: 100%;
  padding: 10px;
  border: 1px solid var(--color-border);
  border-radius: 4px;
  background: var(--color-background-soft);
  color: var(--color-text);
  margin-bottom: 16px;
}

/* ensure checkboxes are not stretched by the generic input rule */
input[type="checkbox"] {
  width: auto;
  height: auto;
  margin: 0;
  vertical-align: middle;
}

button {
  width: 120px;
  padding: 10px 16px;
  border: none;
  border-radius: 4px;
  background: var(--vt-c-indigo);
  color: white;
  cursor: pointer;
  transition: background 0.2s;
}

button:hover {
  background: #1f2d3a;
}

span {
  width: 140px;
  height: 200px;
  background: var(--color-background-mute);
  border: 1px solid var(--color-border);
  display: flex;
  justify-content: center;
  align-items: center;
  font-size: 12px;
  text-align: center;
  padding: 8px;
}

article p {
  margin-bottom: 6px;
}

menu {
  margin-top: 20px;
  display: flex;
  gap: 12px;
  padding: 0px;
}

#guide-box {
  font-size: 14px;
  line-height: 1.5;
  color: var(--color-text);
}

/* Tablets and higher */
@media (min-width: 460px) {
  #book {
    display: flex;
    flex-direction: column;
    align-items: center;
  }
}

/* Tablets and higher */
@media (min-width: 768px) {
  form {
    max-width: 1100px;
    display: grid;
  }
}
</style>
