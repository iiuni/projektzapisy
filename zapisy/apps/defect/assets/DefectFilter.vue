<script lang="ts">
import Vue from "vue";

import TextFilter from "./components/filters/TextFilter.vue";
import LabelsFilter from "./components/filters/LabelsFilter.vue";
import SelectFilter from "./components/filters/SelectFilter.vue";
import CheckFilter from "./components/filters/CheckFilter.vue";

export default Vue.extend({
  components: {
    TextFilter,
    LabelsFilter,
    SelectFilter,
    CheckFilter,
  },
  data: function () {
    return {
      allStates: {
        0: "Zgłoszone",
        1: "W realizacji",
        2: "W oczekiwaniu na realizację",
        3: "Zakończone",
      },
    };
  },
  created: function () {},
});
</script>

<template>
  <div class="card bg-light">
    <div class="card-body">
      <div class="row">
        <div class="col">
          <TextFilter
            filterKey="name-filter"
            :properties="['name']"
            placeholder="Nazwa usterki"
          />
        </div>
        <div class="col">
          <TextFilter
            filterKey="place-filter"
            :properties="['place']"
            placeholder="Miejsce usterki"
          />
        </div>
        <div class="col">
          <LabelsFilter
            title="Stany"
            filterKey="state-filter"
            property="state_id"
            :allLabels="allStates"
            onClass="badge-success"
          />
        </div>
      </div>
    </div>
  </div>
</template>

<style lang="scss" scoped>
.collapsed {
  overflow-y: hidden;
  height: 120px;

  // Blurs over the bottom of filter card.
  &:after {
    position: absolute;
    display: block;
    // Height of the card footer.
    bottom: 28px;
    left: 0;
    height: 50%;
    width: 100%;
    content: "";
    // Bootstrap light colour.
    background: linear-gradient(
      to top,
      rgba(248, 249, 250, 1) 0%,
      rgba(248, 249, 250, 0) 100%
    );
    pointer-events: none; /* so the text is still selectable */
  }
}

// Follows the Bootstrap 4 media query breakpoint.
@media (max-width: 767px) {
  .col-md + .col-md {
    border-top: 1px solid rgba(0, 0, 0, 0.1);
    padding-top: 1em;
  }
}

.card-footer {
  height: 28px;
}
</style>
