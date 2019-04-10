import marked from "marked";
import * as $ from "jquery";

$(".markdown").each(function() {
    const raw = $(this).text().trim();
    const rendered = marked(raw);
    $(this).html(rendered);
});
