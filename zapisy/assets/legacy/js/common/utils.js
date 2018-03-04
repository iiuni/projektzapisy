/**
 * @description determine if an array contains one or more items from another array.
 * @param {array} haystack the array to search.
 * @param {array} arr the array providing items to check for in the haystack.
 * @return {boolean} true|false if haystack contains at least one item from arr.
 */
function findOne(haystack, arr)
{
    return arr.some(function (v) {
        return haystack.indexOf(v) >= 0;
    });
}; 

function stackTrace() {
    var err = new Error();
    return err.stack;
}

function scrollUpToElementIfWindowBelow(selector) {
    const SCROL_TIME = 400;
    const currentWindowTop = $(window).scrollTop();
    const elemTop = $(selector).offset().top;
    if (currentWindowTop > elemTop) {
        $("html, body").animate({ scrollTop: elemTop}, SCROL_TIME);
    }
}
