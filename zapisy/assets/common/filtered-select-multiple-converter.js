import * as $ from "jquery";

window.addEventListener('load',() => {
    const data = JSON.parse($("#filtered-select-multiple-data")[0].innerHTML);
    for(const widget of data){
       let wg = $(widget.id);
       wg.find(".selector-available > h2").addClass("text-light bg-info text-center mb-0").text(widget.txtAvailable)
           .parent().addClass("flex-fill p-0 text-center").removeClass("selector-available")
           .children("select").addClass("form-control").attr('size', widget.size)
           .siblings("a").text("Wybierz wszystkie").parent()
           .find("input").appendTo(wg).addClass("form-control");
       wg.find(".selector-filter").remove();
       wg.find(".selector-chosen > h2").addClass("text-light bg-info text-center mb-0").text(widget.txtChosen)
           .parent().addClass("flex-fill p-0 text-center").removeClass("selector-chosen")
           .children("select").addClass("form-control").attr('size', widget.size)
           .siblings("a").text("Usuń wszystkie");
       wg.children(".selector").addClass("d-flex justify-content-center").removeClass("selector")
           .children(".selector-chooser").addClass("p-2 list-unstyled align-self-center").removeClass("selector-chooser");
    }
 });