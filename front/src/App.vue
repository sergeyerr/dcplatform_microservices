<template>
  <div id="app">
    <nav class="navbar navbar-expand-lg navbar-light bg-light">
      <router-link class="navbar-brand" :to="`/`">
        DCHelper
      </router-link>
      <!--      <p class="navbar-brand">TODOS</p>-->
    </nav>
    <hr />
    <main class="container mt-5">
      <router-view />
    </main>
  </div>
</template>

<script>
export default {
  name: 'App',
};
</script>
