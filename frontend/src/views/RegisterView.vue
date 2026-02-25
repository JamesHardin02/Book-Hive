<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter, RouterLink, useRoute } from 'vue-router'
import BaseButton from '@/components/BaseButton.vue'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const router = useRouter()
const route = useRoute()

const username = ref('')
const email = ref('')
const password = ref('')

async function onSubmit(e: Event) {
  e.preventDefault()
  try {
    await auth.register(username.value.trim(), email.value.trim(), password.value)
    await auth.login(email.value.trim(), password.value.trim())
    const redirect = typeof route.query.redirect === 'string' ? route.query.redirect : '/dashboard'
    router.push(redirect)
  } catch (err) {
    console.log(err)
  }
}

onMounted(() => {
  if (auth.error) {
    auth.error = ''
  }
})
</script>

<template>
  <main>
    <header>
      <img
        src="/src/assets/BookHive-logo-no-text.png"
        style="width: 100px; height: 100px"
        alt="Book Hive Logo"
      />
      <h1>Book Hive</h1>
    </header>
    <div id="register">
      <h2>Register Account</h2>
      <form @submit="onSubmit">
        <input v-model="username" type="text" placeholder="Username" />
        <input v-model="email" type="email" placeholder="Email" />
        <input v-model="password" type="password" placeholder="Password (min 8 chars)" />

        <div v-if="auth.error" style="color: #c00; margin-bottom: 12px">
          <span v-if="!Array.isArray(auth.error)">
            {{ auth.error }}
          </span>

          <span v-else>
            <div v-for="(err, i) in auth.error" :key="i">
              <strong style="font-weight: 700">{{ err.loc[1] }}:</strong> {{ err.msg }}
            </div>
          </span>
        </div>

        <BaseButton
          id="create-now-btn"
          :type="'submit'"
          :message="auth.loading ? 'Creating...' : 'Create Now'"
        />
        <RouterLink to="/">
          <BaseButton type="button" message="Back to Login" />
        </RouterLink>
      </form>
    </div>
    <footer>
      <h3>Member-only tool. All activity is audited.</h3>
    </footer>
  </main>
</template>

<style scoped>
main {
  margin: 0 auto;
}

main header {
  display: flex;
  align-content: center;
  justify-content: center;
  border: 3px solid white;
  padding: 10px;
  border-radius: 10px;
}

main header h1 {
  font-size: 3rem;
  margin-left: 20px;
  margin-top: 10px;
}

img {
  width: 100%;
  aspect-ratio: 16 / 9;
  object-fit: cover;
}

h2 {
  font-size: 2rem;
  margin-bottom: 1rem;
  display: flex;
  justify-content: center;
}

#register {
  margin: 0 22%;
}

form {
  display: flex;
  flex-direction: column;
}

input {
  padding: 0.5rem;
  margin-bottom: 1rem;
  border: 1px solid #ccc;
  border-radius: 4px;
}

footer {
  margin-top: 2rem;
  text-align: center;
  font-size: 1.2rem;
  color: #555;
}

#create-now-btn {
  margin: 15px 0px;
}

/* Tablets and up*/
@media (min-width: 770px) {
  #register {
    margin: 0 25%;
  }
}
</style>
