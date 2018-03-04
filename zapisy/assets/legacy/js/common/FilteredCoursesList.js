/*
 * A base class that represents a filtered list of courses.
 * Inherited and extended by classes that implement the course
 * list page, the schedule prototype and the offer page.
*/

"use strict";

function FilteredCoursesList()
{
    this.init();
};

FilteredCoursesList.getCoursesListFromJson = function(elementName = "courses_list_json")
{
    const jsonString = $("#" + elementName).assertOne().html();
    return JSON.parse(jsonString);
}

FilteredCoursesList.prototype.init = function()
{
    this.initializeTagEffectFilterElems();
};

FilteredCoursesList.prototype.initializeTagEffectFilterElems = function()
{
    // Initialize the tags and effects filter HTML elements
    // (implemented as <select> tags with multiselect)
    // We don't want the users to have to hold ctrl down
    // to be able to select more than one option, so this code below
    // and onMultiselectClicked take care of that.
    let self = this;
    $("#enr-courseFilter-effects option").mousedown(function(e)
    {
        self.onMultiselectClicked(e, this);
        
    });
    $("#enr-courseFilter-tags option").mousedown(function(e)
    {
        self.onMultiselectClicked(e, this);
    });
};

FilteredCoursesList.prototype.onMultiselectClicked = function(e, elem)
{
    e.preventDefault();
    if ($(elem).parent().is(":disabled"))
    {
        return false;
    }
    
    $(elem).attr("selected", !$(elem).attr("selected"));
    $(elem).parent().change();
    return false;
};

FilteredCoursesList.prototype.setCourseVisible = function(course, visible)
{
    course.visible = visible;
    if (visible)
        course.htmlNode.removeClass("hidden");
    else
        course.htmlNode.addClass("hidden");
};


FilteredCoursesList.prototype.initFilters = function()
{
    // Initialize all filters - boilerplate to interact with the
    // filtering library.
	var courseFilterForm = $('#enr-coursesList-top-bar').assertOne();

	courseFilterForm.css('display', 'block');

	courseFilterForm.find('.filter-phrase-reset').assertOne().click(function()
	{
		courseFilterForm.find('.filter-phrase').assertOne().attr('value', '');
	});

	this.noResultsMessageElem = $("#noResultsMessage");
	this.noResultsMessageVisible = false;

    let self = this;

	this.courseFilter = new ListFilter('coursesList-courses', courseFilterForm.getDOM());
	this.courseFilter.afterFilter = function(matchedElementsCount)
	{
		const haveNoResults = (matchedElementsCount == 0);
		self.noResultsMessageVisible = haveNoResults;
        
        if (haveNoResults)
            self.noResultsMessageElem.removeClass("hidden");
        else
            self.noResultsMessageElem.addClass("hidden");
	};

    this.addFilters();
    this.addCustomFilters();

	this.courses.forEach(function(course)
	{
		self.courseFilter.addElement(new ListFilter.Element(course, function(visible)
		{
			var courseToSet = this.data;
			self.setCourseVisible(courseToSet, visible);
		}));
	});

	this.courseFilter.runThread(true);
	$('#enr-coursesList-top-bar').find('label').disableDragging();
};

FilteredCoursesList.prototype.addGeneralFilters = function()
{
    this.courseFilter.addFilter(ListFilter.CustomFilters.createSimpleTextFilter(
		'phrase', '.filter-phrase', function(element, value)
	{
		let course = element.data;
		return (course.name.toLowerCase().indexOf(value.toLowerCase()) >= 0);
	}));

    /*
	this.courseFilter.addFilter(ListFilter.CustomFilters.createSimpleBooleanFilter(
		'hideSigned', '#enr-hidesigned', function(element, value)
	{
		if (!value)
			return true;
		const course = element.data;
		return !course.wasEnrolled;
	}));
	*/
	this.courseFilter.addFilter(ListFilter.CustomFilters.createSimpleBooleanFilter(
		'showEnglish', '#enr-courseFilter-english', function(element, value)
	{
		if(value)
			return true;
		const course = element.data;
		return !course.english;
	}));
	this.courseFilter.addFilter(ListFilter.CustomFilters.createSimpleBooleanFilter(
		'showExam', '#enr-courseFilter-exam', function(element, value)
	{
		if(value)
			return true;
		const course = element.data;
		return !course.exam;
	}));
	this.courseFilter.addFilter(ListFilter.CustomFilters.createSimpleBooleanFilter(
		'showSuggestedForFirstYear', '#enr-courseFilter-suggestedForFirstYear', function(element, value)
	{
		if(!value)
			return true;
		const course = element.data;
		return course.suggested_for_first_year;
	}));

	this.courseFilter.addFilter(ListFilter.CustomFilters.createCourseTypeFilter(
		function(element, courseType)
	{
		const course = element.data;
		return (course.type == courseType);
	}));
};

FilteredCoursesList.prototype.addTagsEffectsFilters = function()
{
    this.courseFilter.addFilter(ListFilter.CustomFilters.createSimpleComboFilter(
		'effects', '#enr-courseFilter-effects', function(element, option)
	{
        if (!option || !$("#effectsSearchEnabled").is(':checked'))
        {
            return true;
        }
        
        const course = element.data;
        let courseEffectsArray =  [].concat(course.effects);
        let selectedEffectsArray = [].concat(option).map(function(num) { return parseInt(num); });
        
        // if no filters in place, match all courses
        // (this happens if the checkbox is checked but the user hasn't selected
        // anything yet)
        if (!selectedEffectsArray.length)
        {
            return true;
        }
        
        // TODO: which should it be? true or false?
        if (!courseEffectsArray.length)
        {
            //return true;
            return false;
        }
        
        return findOne(courseEffectsArray, selectedEffectsArray);
	}));
    
    this.courseFilter.addFilter(ListFilter.CustomFilters.createSimpleComboFilter(
		'tags', '#enr-courseFilter-tags', function(element, option)
	{
        if (!option || !$("#tagsSearchEnabled").is(':checked'))
        {
            return true;
        }
        
        const course = element.data;
        let courseTagsArray = [].concat(course.tags);
        let selectedTagsArray = [].concat(option).map(function(num) { return parseInt(num); });
        
        if (!selectedTagsArray.length)
        {
            return true;
        }
        
        // see above
        if (!courseTagsArray.length)
        {
            //return true;
            return false;
        }
        
        return findOne(courseTagsArray, selectedTagsArray);
	}));
};

FilteredCoursesList.prototype.addFilters = function()
{
    // Install common filters (i.e. all those matching the HTML present in 
    // templates/common/course_list_filters.html).
    this.addGeneralFilters();
    this.addTagsEffectsFilters();
};

// Initialize custom filters - to be overridden by subclasses.
FilteredCoursesList.prototype.addCustomFilters = function()
{ };
