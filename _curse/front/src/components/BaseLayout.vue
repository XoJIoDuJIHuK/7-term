<template>
  <header>
    <h1>Translator App</h1>
    <nav>
      <ul>
        <li><router-link to="/dashboard">Dashboard</router-link></li> 
        <li>User: {{ username }}</li> 
      </ul>
    </nav>
  </header>
  <main>
    <router-view /> 
  </main>
</template>

<script>
export default {
  data() {
    return {
      username: 'Guest'
    }
  }
}
</script>

<style scoped>
main {
  margin-top: 170px;
}

header {
  position: fixed; 
  top: 0;
  left: 0;
  width: 100%;
  background-color: #f0f0f0; 
  padding: 1rem;
}
</style>
