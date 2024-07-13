<script setup lang="ts">
import TextFilter from "./filters/TextFilter.vue";
import SelectFilter from "./filters/SelectFilter.vue";
import CheckFilter from "./filters/CheckFilter.vue";

const allKinds = [
  ["mgr", "Magisterska"],
  ["inż", "Inżynierska"],
  ["lic", "Licencjacka"],
  ["isim", "ISIM"],
  ["lic+inż", "Licencjat+inżynierska"],
  ["lic+inż+isim", "Licencjat+inżynierska+ISIM"],
];

const allStatuses = [
  ["weryfikowana przez komisję", "Weryfikowana przez komisję"],
  ["zwrócona do poprawek", "Zwrócona do poprawek"],
  ["zaakceptowana", "Zaakceptowana"],
  ["w realizacji", "W realizacji"],
  ["obroniona", "Obroniona"],
];
</script>

<template>
  <div class="card bg-light">
    <div class="card-body">
      <div class="row">
        <div class="col-lg-6">
          <TextFilter
            filterKey="title-filter"
            :properties="['title', 'advisor', 'students']"
            placeholder="Nazwa, promotor, studenci"
          />
        </div>
        <div class="col-lg-3">
          <SelectFilter
            filterKey="kind-filter"
            property="kind"
            :options="allKinds"
            placeholder="Typ pracy dyplomowej"
          />
        </div>
        <div class="col-lg-3">
          <SelectFilter
            filterKey="status-filter"
            property="status"
            :options="allStatuses"
            placeholder="Status pracy dyplomowej"
          />
        </div>
      </div>
      <div class="row">
        <div class="col-lg-4">
          <CheckFilter
            filterKey="available-filter"
            property="is_available"
            label="Pokaż tylko niezarezerwowane prace"
          />
        </div>
        <div class="col-lg-4">
          <CheckFilter
            filterKey="mine-filter"
            property="is_mine"
            label="Pokaż tylko moje"
          />
        </div>
      </div>
    </div>
  </div>
</template>
