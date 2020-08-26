<script lang="ts">
// PrototypeDay subclasses the base Day component (`Day.vue`). The only
// difference being, it displays terms with controls using
// TermControlsComponent.
import Component from "vue-class-component";

import DayComponent from "./Day.vue";
import TermControlsComponent from "./TermControls.vue";

@Component({
  components: {
    Term: TermControlsComponent,
  },
})
export default class PrototypeDayComponent extends DayComponent {}
</script>
