<template>
  <div>
    <label for="user_dropdown"><h3>Выберите роль:</h3></label> <br />
    <select v-model="user" name="user_dropdown" id="user_dropdown">
      <option>Пользователь</option>
      <option>Менеджер</option>
      <option>Системный администратор</option>
    </select>
    <hr />
    <div class="card mb-3">
      <div v-if="user === 'Системный администратор'">
        <div class="form-group">
          <label for="sys_admin_prompt">Онтология зависимостей:</label>
          <input
            id="sys_admin_prompt"
            class="form-control-file"
            name="Онтология зависимостей"
            type="file"
            accept=".ont"
            @change="update_dependencies"
          />
        </div>
      </div>

      <div v-if="user === 'Менеджер'">
        <div class="form-group">
          <label for="manager_prompt">Обновить онтологию методов:</label>
          <input
            class="form-control-file"
            id="manager_prompt"
            name="Онтология методов машинного обучения"
            type="file"
            accept=".ont"
            @change="update_methods"
          />
        </div>
        <h3>Существующие методы</h3>
        <ul class="list-group">
          <li
            class="list-group-item"
            v-for="fun in functions"
            :key="fun"
            v-bind:class="{ active: fun === selected }"
            v-on:click="
              selected = fun;
              clear_file();
              get_code_for_method(fun);
            "
          >
            {{ fun }}
          </li>
        </ul>

        <div class="form-group">
          <label for="parameter_prompt"
            >Обновить онтологию параметров выбранного метода:</label
          >
          <input
            class="form-control-file"
            id="parameter_prompt"
            name="Онтология параметров выбранного метода"
            type="file"
            accept=".ont"
            @change="update_param_ontology"
          />
        </div>

        <h3>Код для запуска метода</h3>
        <button
          type="button"
          class="btn btn-success"
          v-bind:class="{ disabled: selected === '' }"
          v-on:click="save_code()"
        >
          Сохранить код
        </button>
        <prism-editor
          v-bind="{ hidden: selected === '' }"
          class="my-editor height-200"
          v-model="code"
          :highlight="highlighter"
          line-numbers
        ></prism-editor>
      </div>

      <div v-if="user === 'Пользователь'">
        <h3>Существующие методы</h3>
        <ul class="list-group">
          <li
            class="list-group-item"
            v-for="fun in functions"
            :key="fun"
            v-bind:class="{ active: fun === selected }"
            v-on:click="
              selected = fun;
              params_getter(fun);
            "
          >
            {{ fun }}
          </li>
        </ul>
        <hr />
        <button
          type="button"
          class="btn btn-primary"
          v-on:click="run_selected_method"
          v-bind="{ hidden: selected === '' }"
        >
          Запуск метода
        </button>
        <hr />
        <h3>Параметры</h3>
        <table class="table">
          <thead class="thead-dark">
            <tr>
              <th scope="col">Имя параметра</th>
              <th scope="col">Тип параметра</th>
              <th scope="col">Домен параметра</th>
              <th scope="col">Класс параметра</th>
              <th scope="col">Значение параметра</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="param in params" :key="param.name">
              <th scope="row">{{ param.name }}</th>
              <td>{{ param.type }}</td>
              <td>{{ param.domain }}</td>
              <td>{{ param.class }}</td>
              <td>
                <input
                  type="text"
                  class="form-control"
                  placeholder="Value"
                  v-model="param.value"
                  aria-label="value"
                  aria-describedby="basic-addon1"
                />
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script>
const Prism = require('prismjs');
const axios = require('axios');
// eslint-disable-next-line no-unused-vars
const loadLanguages = require('prismjs/components/');
export default {
  name: 'TodosListPage',

  data() {
    return {
      functions: ['test1', 'test2'],
      params: [],
      user: 'Пользователь',
      code: 'Print(1)',
      selected: '',
    };
  },

  async mounted() {
    axios
      .get('http://localhost/get_methods')
      .then(response => (this.functions = response.data));
  },
  methods: {
    clear_file() {
      document.getElementById('parameter_prompt').value = null;
    },

    highlighter(code) {
      // js highlight example
      return Prism.highlight(code, Prism.languages.js, 'js');
    },

    params_getter(method_name) {
      axios
        .get(`http://localhost/get_params/${method_name}/`)
        .then(response => (this.params = response.data));
    },

    async update_dependencies(event) {
      let formData = new FormData();
      formData.append('file', event.target.files[0]);
      await axios({
        method: 'post',
        url: 'http://localhost/upload_dependencies_ontology',
        data: formData,
        headers: {
          'Content-Type': `multipart/form-data`,
        },
      });
    },

    async update_methods(event) {
      let formData = new FormData();
      formData.append('file', event.target.files[0]);
      await axios({
        method: 'post',
        url: 'http://localhost/upload_methods_ontology',
        data: formData,
        headers: {
          'Content-Type': `multipart/form-data`,
        },
        // eslint-disable-next-line no-unused-vars
      }).then(request => {
        axios
          .get('http://localhost/get_methods')
          .then(response => (this.functions = response.data));
      });
    },

    async update_param_ontology(event) {
      console.log(event.target.files[0]);
      let formData = new FormData();
      formData.append('file', event.target.files[0]);
      await axios({
        method: 'post',
        url: `http://localhost/upload_params_ontology/${this.selected}/`,
        data: formData,
        headers: {
          'Content-Type': `multipart/form-data`,
        },
      });
    },

    async get_code_for_method(method) {
      axios
        .get(`http://localhost/get_script/${method}/`)
        .then(response => (this.code = response.data.script));
    },

    async save_code() {
      const json = JSON.stringify({ script: this.code });
      await axios.post(
        `http://localhost/write_script/${this.selected}/`,
        json,
        {
          headers: {
            // Overwrite Axios's automatically set Content-Type
            'Content-Type': 'application/json',
          },
        },
      );
    },

    async get_libs_for_method(method_name) {
      return axios
        .get(`http://localhost/get_libraries/${method_name}/`)
        .then(response => response.data);
    },

    async get_image(deps) {
      const json = JSON.stringify(deps);
      return axios
        .post(`http://localhost/gen_image_script`, json, {
          headers: {
            // Overwrite Axios's automatically set Content-Type
            'Content-Type': 'application/json',
          },
        })
        .then(response => response.data.img_code);
    },

    async run_prox(code, img, data = 'data.csv') {
      const json = JSON.stringify({ code: code, img: img, data: data });
      await axios
        .post(`http://localhost/run`, json, {
          headers: {
            // Overwrite Axios's automatically set Content-Type
            'Content-Type': 'application/json',
          },
        })
        // eslint-disable-next-line no-unused-vars
        .then(response => alert('your script is wrong'))
        .catch(error => console.log(error.response));
    },
    async run_selected_method() {
      let method = this.selected;
      let image = null;
      this.get_libs_for_method(method)
        .then(response => {
          return this.get_image(response);
        })
        .then(response => {
          image = response;
          return this.get_code_for_method(method);
        })
        // eslint-disable-next-line no-unused-vars
        .then(_ => {
          this.run_prox(this.code, image);
        });
    },
  },
};
</script>

<style scoped></style>
