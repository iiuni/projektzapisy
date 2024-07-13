<script lang="ts">
// PrototypeDay subclasses the base Day component (`Day.vue`). The only
// difference being, it displays terms with controls using
// TermControlsComponent.
import Component from "vue-class-component";

import Day from "./Day.vue";
import TermControls from "./TermControls.vue";

@Component({
  components: {
    Term: TermControls,
  },
})
export default class PrototypeDay extends Day {}
</script>
