import * as $ from "jquery";

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

const orderClasses = ["fa-sort-up", "fa-sort-down", "fa-sort"];

$(function () {
  $(".table .headers").each((i, headers) => {
    const proposals = $(".table .proposals").eq(i);
    const ths = $(headers).find("th").slice(0, 3);
    let col = 0;
    let order = 0;
    $(ths).each((j, th) => {
      const text = $(th).text();
      if (j === col) {
        $(th)
          .empty()
          .append(
            `<div class="th-content">${text}<i class="fa fa-sort-up"></i></div>`
          );
        sort(proposals, col, order);
      } else {
        $(th)
          .empty()
          .append(
            `<div class="th-content">${text}<i class="fa fa-sort"></i></div>`
          );
      }
      $(th).on("click", () => {
        if (j === col) {
          order = (order + 1) % 2;
          $(th)
            .find("[data-fa-i2svg]")
            .removeClass(orderClasses)
            .addClass(orderClasses[order]);
        } else {
          $(ths)
            .eq(col)
            .find("[data-fa-i2svg]")
            .removeClass(orderClasses)
            .addClass(orderClasses[2]);
          $(th)
            .find("[data-fa-i2svg]")
            .removeClass(orderClasses)
            .addClass(orderClasses[0]);
          col = j;
          order = 0;
        }
        sort(proposals, col, order);
      });
    });
  });
});
