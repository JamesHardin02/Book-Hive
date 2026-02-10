<template>
  <div class="main-menu">
    <header>
      <img src="/src/assets/BookHive-logo-no-text.png" style='width: 100px; height: 100px' alt="Book Hive Logo" />
      <h1>Book Hive</h1>
    </header>
    <div class="sign-in">
      <h2>Sign In</h2>
      <form>
        <input type="text" placeholder="Username" />
        <input type="password" placeholder="Password" />
        <button type="submit">Sign In</button>
      </form>
    </div>
    <footer>
      <h3>Member-only tool. All activity is audited.</h3>
  </footer>
  </div>
</template>

<style>
  .main-menu {
    margin: 0 auto;
  }
  .main-menu header{
    display: flex;
    align-content: center;
    justify-content: center;
    border: 3px solid white;
    padding: 10px;
    border-radius: 10px;
  }
  .main-menu header h1{
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
  .sign-in form {
    display: flex;
    flex-direction: column;
  }
  input {
    padding: 0.5rem;
    margin-bottom: 1rem;
    border: 1px solid #ccc;
    border-radius: 4px;
  }
  button {
    padding: 0.5rem;
    background-color: #e8c456;
    color: white;
    border: none;
    border-radius: 4px;
    cursor: pointer;
  }
  button:hover {
    background-color: #d4b04a;
  }
  footer {
    margin-top: 2rem;
    text-align: center;
    font-size: 1.2rem;
    color: #555;
  }

</style>
