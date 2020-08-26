<script lang="ts">
// PrototypeTimetable is the same as SimpleTimetable with a difference, that it
// displays the day using PrototypeDay component rather than Day component.
import Component from "vue-class-component";

import SimpleTimetable from "./SimpleTimetable.vue";
import PrototypeDay from "./PrototypeDay.vue";

@Component({
  components: {
    Day: PrototypeDay,
  },
})
export default class PrototypeTimetable extends SimpleTimetable {}
</script>
