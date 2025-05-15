<template>
  <div class="app">
    <h1>Bioinformatics Tool</h1>
    <form @submit.prevent="handleSubmit">
      <textarea v-model="sequence" placeholder="Paste FASTA sequence here..."></textarea>
      <br />
      <button type="submit">Align</button>
    </form>

    <div v-if="result">
      <h2>Result:</h2>
      <pre>{{ result }}</pre>
    </div>
  </div>
</template>

<script>
export default {
  name: 'App',
  data() {
    return {
      sequence: '',
      result: ''
    };
  },
  methods: {
    async handleSubmit() {
      const response = await fetch(`${import.meta.env.VITE_API_URL}/upload-fasta`, {
        method: 'POST',
        body: this.buildFormData()
      });
      const data = await response.json();
      this.result = data.alignment;
    },
    buildFormData() {
      const formData = new FormData();
      const blob = new Blob([this.sequence], { type: 'text/plain' });
      formData.append('fasta_file', blob, 'input.fasta');
      return formData;
    }
  }
};
</script>

<style>
.app {
  padding: 2rem;
  font-family: sans-serif;
}
textarea {
  width: 100%;
  height: 150px;
}
button {
  margin-top: 1rem;
  padding: 0.5rem 1rem;
}
</style>
