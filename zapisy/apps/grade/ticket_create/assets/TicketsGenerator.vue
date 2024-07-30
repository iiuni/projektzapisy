<script setup lang="ts">
import { ref } from "vue";
import generateTicketsMain from "./ticketsgenerate";

const ticketGenerationFinished = ref(false);
const tickets = ref("");
const loading = ref(false);
const exception = ref(false);
// TODO type errors correctly (not with any)
const errors = ref<any[]>([]);

const generateTicketsOnClick = async () => {
  loading.value = true;
  try {
    tickets.value = await generateTicketsMain();
  } catch (e: any) {
    errors.value = [e.response.data];
    exception.value = true;
  }
  loading.value = false;
  ticketGenerationFinished.value = true;
};
const copyTickets = () => {
  let ticketsTextArea = document.getElementById("tickets") as HTMLInputElement;
  ticketsTextArea.select();
  // TODO execCommand is deprecated - replace with Clipboard API?
  document.execCommand("copy");
};
</script>

<template>
  <div class="text-center">
    <button
      id="tickets_generate_button"
      class="btn btn-primary"
      v-if="!ticketGenerationFinished"
      @click="generateTicketsOnClick"
      :disabled="loading"
    >
      <span v-if="loading" class="spinner-border spinner-border-sm me-1"></span
      >Pobierz klucze
    </button>
    <div v-if="ticketGenerationFinished">
      <div id="grade-tickets-save-form">
        <div v-if="!exception">
          <h3>Pomyślnie wygenerowano klucze.</h3>
          <h3>
            Zapisz je w bezpiecznym miejscu -
            <strong>nie ma powrotu do tego ekranu</strong>.
          </h3>
          <br />
          <div class="text-center">
            <button id="copy-keys" class="btn btn-primary" @click="copyTickets">
              Skopiuj
            </button>
          </div>
          <br />
          <textarea
            ref="tickets-textarea"
            id="tickets"
            name="tickets"
            v-model="tickets"
            style="width: 1000px; height: 400px"
          ></textarea>
        </div>
        <div class="alert alert-danger" v-for="msg in errors" :key="msg.id">
          Błąd: {{ msg }}
        </div>
      </div>
    </div>
  </div>
</template>

<style lang="sass" scoped>
.ticket-error
{
	border: 1px solid #cccccc;
	background: #FFF5B3;
	font-size: 14px;
	-moz-border-radius: 4px;
	-webkit-border-radius: 4px;
	border-radius: 4px;
  margin: 10px;
	margin-bottom: 10px;
	padding: 10px 10px;
}
</style>
