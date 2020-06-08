<script lang="ts">
import Vue from "vue";
import Component from "vue-class-component";

import TextFilter from "./filters/TextFilter.vue";
import SelectFilter from "./filters/SelectFilter.vue";
import CheckFilter from "./filters/CheckFilter.vue";

export default Vue.extend({
  components: {
    TextFilter,
    SelectFilter,
    CheckFilter
  },
  data: function() {
    return {
      allKinds: {}
    };
  },
  created: function() {
    this.allKinds = [
      ["mgr", "Magisterska"],
      ["inż", "Inżynierska"],
      ["lic", "Licencjacka"],
      ["isim", "ISIM"],
      ["lic+inż", "Licencjat+inżynierska"],
      ["lic+inż+isim", "Licencjat+inżynierska+ISIM"]
    ];
    this.allStatuses = [
      [0, "W trakcie weryfikacji"],
      [1, "Zaakceptowane"]
    ];
  }
});
</script>

<template>
  <div class="card bg-light">
    <div class="card-body">
      <div class="row">
        <div class="col-lg">
          <TextFilter
            filterKey="title-filter"
            property="title"
            placeholder="Nazwa pracy dyplomowej"
          />
        </div>
        <div class="col-lg">
          <TextFilter
            filterKey="advisor-filter"
            property="advisor"
            placeholder="Promotor"
          />
        </div>
        <div class="col-lg">
          <SelectFilter
            filterKey="kind-filter"
            property="kind"
            :options="allKinds"
            placeholder="Typ pracy dyplomowej"
          />
        </div>
      </div>
      <div class="row">
        <div class="col-lg">
          <CheckFilter
            filterKey="available-filter"
            property="is_available"
            label="Pokaż tylko dostępne prace"
          />
        </div>
        <div class="col-lg">
          <CheckFilter
            filterKey="mine-filter"
            property="is_mine"
            label="Pokaż tylko moje"
          />
        </div>
        <div class="col-lg"></div>
      </div>
    </div>
  </div>
</template>
