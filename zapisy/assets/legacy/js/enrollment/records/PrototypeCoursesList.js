/*
 * Schedule prototype courses list.
*/

"use strict";

function PrototypeCoursesList()
{
    this.courseList = [];
    
    FilteredCoursesList.call(this);
};

PrototypeCoursesList.prototype = Object.create(FilteredCoursesList.prototype);

PrototypeCoursesList.prototype.init = function()
{
    FilteredCoursesList.prototype.init.call(this);
	
    var scheduleContainer = $('#enr-schedulePrototype-scheduleContainer').assertOne();
    // This object is responsible for the business logic.
    // It implements the pinning functionality and allows users
    // to sign up for courses or leave course groups.
    this.schedule = new Schedule(scheduleContainer);
    
    // Whether the user is still allowed to leave a course group
    // they've signed up for.
    const leavingAllowedStr = $('#isLeavingAllowed').val();
	Fereol.Enrollment.isLeavingAllowed = (leavingAllowedStr.toLowerCase() === 'true');
    
    if( user_is_student )
    {
        // TODO: this didn't work anyway (tried to use an undefined var);
        // to be fixed in the future.
        // this.initRecordsLocking();
    }
    
    this.initCourses();
    this.initGroups();
    this.processGroupsAndTerms();
    
    this.uncheckAllButton = $("#enr-schedulePrototype-uncheckAll");
    this.uncheckAllButton.disableDragging();
    let self = this;
    this.uncheckAllButton.click(function()
	{
		self.courseList.forEach(function(course)
		{
			course.setPrototyped(false);
		});
	});
};

PrototypeCoursesList.prototype.initCourses = function()
{
    this.courses = FilteredCoursesList.getCoursesListFromJson();
    
    let self = this;
    this.courses.forEach(function(course)
    {
        self.processCourse(course);
    });
    
    this.initFilters();
};

PrototypeCoursesList.prototype.processCourse = function(courseRawObj)
{
    // Create a course object for use by the Schedule-related
    // code that actually implements the prototype functionality.
    Fereol.Enrollment.Course.fromJSON(courseRawObj);
    
    // Create a course object for use by the legacy prototype code
    // Copy the keys of the JSON object since we'll also be adding
    // some custom stuff.
    let course = new PrototypeCourse();
    Object.keys(courseRawObj).forEach(function(key) {
        course[key] = courseRawObj[key];
    });
    
    // Find the related DOM nodes (needed for capturing events
    // and hiding the course in response to filter events)
    let courseCheckbox = $("#checkbox-course-" + course.id);    
    let containingListItem = $("#listItem-course-" + course.id);
    
    courseRawObj.htmlNode = containingListItem;
    
    // Needed by legacy schedule prototype code
    course._prototypedCheckbox = courseCheckbox;
    this.courseList.push(course);
};

PrototypeCoursesList.prototype.processGroupsAndTerms = function()
{
    let self = this;
    this.courseList.forEach(function(course)
    {
        let termsObjects = course.terms;
        course.terms = [];
        termsObjects.forEach(function(termObj)
        {
            let sterm = Fereol.Enrollment.ScheduleCourseTerm.fromObject(termObj);
            sterm.displayStyle =
                Fereol.Enrollment.ScheduleCourseTerm.DisplayStyle.PROTOTYPE;

            sterm.assignSchedule(self.schedule);
            course.terms.push(sterm);
        });
        (function()
		{
			course._prototypedCheckbox.click(function()
			{
				course.setPrototyped(course._prototypedCheckbox.attr('checked'));
			});
		})();
        course.setPrototyped(course._prototypedCheckbox.attr('checked'));
    });
};


PrototypeCoursesList.prototype.initRecordsLocking = function()
{
    // Not used right now. Has a bug below (self._updateVisibility();)
    // - self is not defined. TODO: fix at a later date and re-enable.
	var lockForm = $('#enr-schedulePrototype-setLocked').assertOne();
	var lockURL = lockForm.find('input[name=ajax-url]').assertOne().
		attr('value').trim();
	var isLocked = (lockForm.find('input[name=lock]').assertOne().
		attr('value') != 'true');
	var isLocking = false;

	var lockButton = $.create('a').insertAfter(lockForm);
	lockForm.remove();
	lockButton.attr('id', 'enr-schedulePrototype-setLocked');

	var updateLockButton = function()
	{
		var label = (isLocked ? 'Odblokuj' : 'Zablokuj') + ' plan';
		lockButton.text(label).attr('title', label).
			toggleClass('locked', isLocked).
			toggleClass('unlocked', !isLocked);
	};
	updateLockButton();

	lockButton.click(function()
	{
		if (isLocking)
			return;
		isLocking = true;
		lockButton.css('opacity', '0.5');

		isLocked = !isLocked;
		updateLockButton();
		if( user_is_student ){
		$.post(lockURL, {
			lock: isLocked
		}, function(data)
		{
			var result = AjaxMessage.fromJSON(data);
			self._isLoading = false;
			if (result.isSuccess())
			{
				isLocking = false;
				lockButton.css('opacity', '1');
			}
			else
				result.displayMessageBox();
			self._updateVisibility();
		}, 'json');
        }
	});

	lockButton.hover(function()
	{
		if (isLocking)
			return;
		lockButton.
			toggleClass('locked', !isLocked).
			toggleClass('unlocked', isLocked);
	}, function()
	{
		if (isLocking)
			return;
		lockButton.
			toggleClass('locked', isLocked).
			toggleClass('unlocked', !isLocked);
	})
};

PrototypeCoursesList.prototype.initGroups = function()
{
	const groupsRAW = JSON.parse($('#courses_groups').html());
	groupsRAW.forEach(function(groupRAW)
	{
		Fereol.Enrollment.CourseGroup.fromJSON(groupRAW);
	});
};


$(document).ready(function()
{
    new PrototypeCoursesList();
});


// Used by legacy code.
function PrototypeCourse()
{
	this.model = null; // model danych

	this.wasEnrolled = null;
	this.english = null;
	this.exam = null;
	this.suggested_for_first_year = null;
	this.terms = [];
	this.isPrototyped = false;
	this._prototypedCheckbox = null;
};

PrototypeCourse.prototype.setPrototyped = function(prototyped)
{
	prototyped = !!prototyped;
	if (this.isPrototyped == prototyped)
		return;
	this.isPrototyped = prototyped;
	this._prototypedCheckbox.attr('checked', prototyped);

	this.terms.forEach(function(term)
	{
		term.setPrototyped(prototyped);
	});
};
