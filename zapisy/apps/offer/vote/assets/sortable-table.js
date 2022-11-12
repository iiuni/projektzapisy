import * as $ from "jquery";
import "tablesorter";

$(function () {
  const collator = new Intl.Collator("pl");
  $(".table").tablesorter({
    // sort first column in ascending order
    sortList: [[0, 0]],
    // set up proper sorting of words containing polish letters
    textSorter: function (a, b) {
      return collator.compare(a, b);
    },
    // set up icons indicating sorting order
    headerTemplate: "{content}{icon}",
    cssIcon: "tablesorter-icon",
    cssIconAsc: "fa fa-sort-up",
    cssIconDesc: "fa fa-sort-down",
    cssIconNone: "fa fa-sort",
  });
});
