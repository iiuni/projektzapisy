import Vue from "vue";
import CounterComponent from "./components/CounterComponent.vue";

// comp will hold a Vue component.
let comp: CounterComponent | null = null;

// Given a name-value map and an input DOM element updates the value
// corresponding to the input.
function setValueMapFromInput(
  map: { [key: string]: number },
  input: HTMLInputElement
) {
    const name: string = input.getAttribute("name");
    const val: number = parseInt(input.value, 10);
    map[name] = val;
}

function setUpCounter() {
    const limit = parseInt(
      document.getElementById("point-counter").innerHTML, 10
    );
    const inputs = document.querySelectorAll(".limit select");

    // For every input (under class .limit) we store its value in inputsMap.
    let inputsMap: {[key: string]: number} = {};
    for (const input of inputs) {
        setValueMapFromInput(inputsMap, input as HTMLInputElement);
    }

    comp = new Vue({
        el: "#point-counter",
        data: {
            inputs: inputsMap,
            limit: limit,
        },
        render: function (h) {
            return h(CounterComponent, {
                props: {
                    inputs: this.inputs,
                    limit: this.limit,
                }
            });
        }
    });
}

document.addEventListener("DOMContentLoaded", function() {
    // We set-up the counter component in the beginning.
    setUpCounter();

    // Whenever one of the inputs is changed, we need to update the value stored
    // in the component.
    const inputs = document.querySelectorAll(".limit select");
    for (const input of inputs) {
        (input as HTMLInputElement).addEventListener("input", function(_) {
            setValueMapFromInput((comp as CounterComponent).inputs, this);
        });
    }
});
