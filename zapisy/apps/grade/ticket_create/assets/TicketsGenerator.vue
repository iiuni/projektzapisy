<script lang="ts">
import Vue from "vue";
import Component from "vue-class-component";
import generateTicketsMain from "./ticketsgenerate";

@Component
export default class TicketsGenerator extends Vue {
  ticketGenerationFinished: boolean = false;
  tickets: string = "";
  loading: boolean = false;
  exception: boolean = false;
  errors: string[] = new Array();
  async generateTicketsOnClick() {
    this.loading = true;
    try {
      this.tickets = await generateTicketsMain();
    } catch (e) {
      this.errors = [e.response.data];
      this.exception = true;
    }
    this.loading = false;
    this.ticketGenerationFinished = true;
  }
  copyTickets() {
    let ticketsTextArea = this.$refs["tickets-textarea"] as HTMLInputElement;
    ticketsTextArea.select();
    document.execCommand("copy");
  }
}
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
      <span v-if="loading" class="spinner-border spinner-border-sm mr-1"></span
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
            style="width:1000px; height:400px"
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
