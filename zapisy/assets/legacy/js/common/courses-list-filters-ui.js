function effectsTagsFiltersToggled()
{
    var filtersVisibility = $("#tagsEffectsFilters").css("display");

    if (filtersVisibility === "none")
    {
        $("#tagsEffectsFilters").css("display", "block");
        $("#tagsEffectsFiltersToggle").text("ukryj filtry efektów/tagów");
    }

    else
    {
        $("#tagsEffectsFilters").css("display", "none");
        $("#tagsEffectsFiltersToggle").text("pokaż filtry efektów/tagów");
    }
}

function unselectAllOptions(listId)
{
    $("#enr-courseFilter-" + listId + " option").each(function()
    {
        $(this).removeAttr("selected");
    });
}

// TODO: should we unselect when the filters are hidden?
function onEffectsFilterToggled()
{
    unselectAllOptions("effects", false);

    if ($("#effectsSearchEnabled").is(":checked"))
    {
        $("#enr-courseFilter-effects").removeAttr("disabled");
        $('#enr-courseFilter-effects').change();
    }

    else
    {
        $('#enr-courseFilter-effects').change();
        $("#enr-courseFilter-effects").attr("disabled", "disabled");
    }
}

function onTagsFilterToggled()
{
    unselectAllOptions("tags", false);

    if ($("#tagsSearchEnabled").is(":checked"))
    {
        $("#enr-courseFilter-tags").removeAttr("disabled");
        $('#enr-courseFilter-tags').change();
    }

    else
    {
        $('#enr-courseFilter-tags').change();
        $("#enr-courseFilter-tags").attr("disabled", "disabled");
    }
}

function getCourseIdFromIdString(idString)
{
    let chunks = idString.split("-");
    return parseInt(chunks[3]);
}

function onCourseMiddleMouseClick(sender)
{
    let tagName = sender.attr("tagName").toLowerCase();
    let idString = "";
    if (tagName === "label")
    {
        idString = sender.attr("for");
    }
    else if (tagName === "input")
    {
        idString = sender.attr("id");
    }
    
    let ourCourseId = getCourseIdFromIdString(idString);
    $.each($("#typeFilterList input[type='checkbox']"), function(i, val)
    {
        let checkboxElem = $(val);
        let curId = getCourseIdFromIdString(checkboxElem.attr("id"));
        if (curId !== ourCourseId)
        {
            checkboxElem.attr("checked", "");
        }
    });
    
    let checkboxForThisId = $("#filter-course-type-" + ourCourseId);
    checkboxForThisId.attr("checked", "true");
}

$(document).ready(function()
{
    unselectAllOptions("effects", false);
    unselectAllOptions("tags", false);
    
    $(".courseTypeClickable").mousedown(function(e) {
        if (e.which === 2)
        {
            onCourseMiddleMouseClick($(this));
            return false;
        }
        return true;
    });
});
