<script setup lang="ts">
import PageHeader from '@/components/PageHeader.vue'
</script>

<template>
  <PageHeader page="Checkout / Record Sale" />

  <div class="checkout-container">
    <div class="section">
      <h2>Member Lookup</h2>

      <label>Enter Member Name Here:</label>
      <input type="text" placeholder="Type member name..." />

      <label>Select Member's ID:</label>
      <select>
        <option value="">— Select ID —</option>
        <option>00012</option>
        <option>00059</option>
      </select>

      <button>Register Member</button>
    </div>

    <div class="section">
      <h2>Checkout / Record Sale Guide</h2>
      <div class="guide-box">
        <p>If more than one member has the same name, select their ID.</p>
        <p>If only 1 ID is present it is automatically selected.</p>
        <p>
          If no IDs are present, for book checkout this person must be registered for membership.
        </p>
        <p>To record the sale of this book, membership is optional.</p>
      </div>
    </div>

    <div class="section full">
      <div class="book-section">
        <div class="book-cover">BOOK COVER<br />PLACEHOLDER</div>

        <div class="book-details">
          <p><strong>Title:</strong> Lorem Ipsum</p>
          <p><strong>Author:</strong> Jane Doe</p>
          <p><strong>ISBN:</strong> 123-3-3893-9292-2</p>
          <p><strong>Year:</strong> Earliest – 1998; Latest – 2001</p>
          <p><strong>Aisle:</strong> B</p>
          <p><strong>Shelf:</strong> 2</p>

          <div class="action-buttons">
            <button>Checkout</button>
            <button>Record Sale</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.checkout-container {
  max-width: 1100px;
  margin: 40px auto;
  padding: 24px;
  background: var(--color-background-soft);
  border: 1px solid var(--color-border);
  border-radius: 8px;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 32px;
}

.section {
  padding: 20px;
  background: var(--color-background);
  border: 1px solid var(--color-border);
  border-radius: 6px;
}

.section.full {
  grid-column: span 2;
}

h2 {
  margin-bottom: 12px;
  color: var(--color-heading);
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

button {
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

.guide-box {
  font-size: 14px;
  line-height: 1.5;
  color: var(--color-text);
}

.book-section {
  display: flex;
  gap: 20px;
  align-items: flex-start;
}

.book-cover {
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

.book-details p {
  margin-bottom: 6px;
}

.action-buttons {
  margin-top: 20px;
  display: flex;
  gap: 12px;
}
</style>
