import Vue from "vue";
import CounterComponent from "./components/CounterComponent";

var comp;

function setUpCounter() {
    const limit = parseInt($("#point-counter").text());
    const inputs = $(".limit select");
    
    let inputsMap = {};
    inputs.each((_, input) => {
        inputsMap[$(input).attr("name")] = parseInt($(input).val());
    });

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

$(() => {
    setUpCounter();
});

$(".limit select").change(function() {
    const name = $(this).attr("name");
    const val = parseInt($(this).val());
    comp.inputs[name] = val;
})
