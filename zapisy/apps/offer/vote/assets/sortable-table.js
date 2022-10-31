import * as $ from "jquery";

// col - column to be sorted
// order - ascending (0) or descending (1)
function sort(proposals, col, order) {
  const sorted = $(proposals)
    .find("tr")
    .toArray()
    .sort((tr1, tr2) => {
      let a = $(tr1).find("td").eq(col).text();
      let b = $(tr2).find("td").eq(col).text();
      if (order === 1) {
        [a, b] = [b, a];
      }
      // the first column contains text
      if (col === 0) {
        return new Intl.Collator("pl").compare(a, b);
      } else {
        a = Number(a);
        b = Number(b);
        if (a < b) {
          return -1;
        } else if (a > b) {
          return 1;
        }
        return 0;
      }
    });
  $(proposals).empty().append(sorted);
}

// fontawesome classes
// orderClasses[0] - class for ascending order
// orderClasses[1] - class for descending order
// orderClasses[2] - class for no order
const orderClasses = ["fa-sort-up", "fa-sort-down", "fa-sort"];

$(function () {
  $(".table .headers").each((i, headers) => {
    // get proposals for the current headers
    const proposals = $(".table .proposals").eq(i);
    // ignore the last column
    const ths = $(headers).find("th").slice(0, 3);
    // initially proposals are sorted by the first column in ascending order
    let col = 0;
    let order = 0;

    $(ths).each((j, th) => {
      const text = $(th).text();
      if (j === col) {
        // insert the icon and text into a flexbox container
        $(th)
          .empty()
          .append(
            `<div class="th-content">${text}<i class="fa ${orderClasses[0]}"></i></div>`
          );
        // initial sort
        sort(proposals, col, order);
      } else {
        $(th)
          .empty()
          .append(
            `<div class="th-content">${text}<i class="fa ${orderClasses[2]}"></i></div>`
          );
      }

      $(th).on("click", () => {
        // the th is in the column that the proposals are sorted by
        if (j === col) {
          // toggle between ascending and descending order
          order = (order + 1) % 2;
          // update the icon
          $(th)
            .find("[data-fa-i2svg]")
            .removeClass(orderClasses)
            .addClass(orderClasses[order]);
        } else {
          // update the icons
          $(ths)
            .eq(col)
            .find("[data-fa-i2svg]")
            .removeClass(orderClasses)
            .addClass(orderClasses[2]);
          $(th)
            .find("[data-fa-i2svg]")
            .removeClass(orderClasses)
            .addClass(orderClasses[0]);
          // update the column and set the order to ascending
          col = j;
          order = 0;
        }
        sort(proposals, col, order);
      });
    });
  });
});
