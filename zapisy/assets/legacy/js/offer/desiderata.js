document.addEventListener("DOMContentLoaded", function() {
    function handleClick (event) {
        event.preventDefault();
        var tr = this.parentNode.parentNode;
        var checkboxes = Array.prototype.slice.call(
            tr.querySelectorAll('input[type=checkbox]')
        );
        if (checkboxes.some(function (el) { return !el.checked }))
            checkboxes.forEach(function (el) { el.checked = true });
        else
            checkboxes.forEach(function (el) { el.checked = false });
    }
    (function () {
        var togglers = document.getElementsByClassName('desiderata-toggler');
        var idx;
        for(idx = 0; idx < togglers.length; idx += 1) {
            togglers[idx].addEventListener('click', handleClick);
        }
    })();
});
