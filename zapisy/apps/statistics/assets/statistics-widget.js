import { createApp } from "vue";
import StatisticsList from "./components/StatisticsList.vue";
import StatisticsFilter from "./components/StatisticsFilter.vue";
import store from "./store";

if (document.getElementById("statistics-filter") !== null) {
  const statisticsFilterApp = createApp(StatisticsFilter);
  statisticsFilterApp.use(store);
  statisticsFilterApp.mount("#statistics-filter");
}

if (document.getElementById("statistics-list") !== null) {
  const statisticsListApp = createApp(StatisticsList);
  statisticsListApp.use(store);
  statisticsListApp.mount("#statistics-list");
}
