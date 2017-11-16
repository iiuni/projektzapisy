/**
 * Kod odpowiedzialny za plan zajęć.
 */

UserScheduleView = new Object();

/**
 * Inicjuje widok planu.
 */

UserScheduleView.init = function()
{
	if ($('div#student-profile > table.table-info').length == 0)
		return;

	UserScheduleView.initGroups();

	var scheduleContainer = $('#user-schedule-scheduleContainer').assertOne();

	UserScheduleView.schedule = new Schedule(scheduleContainer, {
		dayColumnWidth: 115
	});

	UserScheduleView.initCourseList();
};
$(UserScheduleView.init);

UserScheduleView.courseList = [];

UserScheduleView.initGroups = function()
{
	const coursesRAW = JSON.parse($(
		"#user-schedule-courses-json").html());
	coursesRAW.forEach(function(courseRAW)
	{
		Fereol.Enrollment.Course.fromJSON(courseRAW);
	});

	const groupsRAW = JSON.parse($(
		"#user-schedule-groups-json").html());
	groupsRAW.forEach(function(groupRAW)
	{
		Fereol.Enrollment.CourseGroup.fromJSON(groupRAW);
	});
};

UserScheduleView.initCourseList = function()
{
	var courseList = $('#user-schedule-listByCourse');

	courseList.find('span').each(function(idx, elem)
	{
		elem = $(elem);

		var course = new UserScheduleView.Course();
		UserScheduleView.courseList.push(course);

		course.model = Fereol.Enrollment.Course.getByID(
			elem.children('input[name=id]').attr('value').castToInt());

		course._listElementContainer = elem;

		elem.find('input[name=term]').each(function(idx, elem)
		{
			elem = $(elem);

			var sterm = Fereol.Enrollment.ScheduleCourseTerm.fromJSON(elem.attr('value'));
			sterm.displayStyle =
				Fereol.Enrollment.ScheduleCourseTerm.DisplayStyle.SCHEDULE;

			sterm.assignSchedule(UserScheduleView.schedule);

			course.terms.push(sterm);
		});
	});
};

/*******************************************************************************
 * Klasa przedmiotu używanego w planie, tzn posiadającego kolekcję terminów.
 ******************************************************************************/

UserScheduleView.Course = function()
{
	this.model = null; // model danych
	
	this.terms = [];
	this._listElementContainer = null;
	this._prototypedCheckbox = null;
};

UserScheduleView.Course.prototype.toString = function()
{
	return 'UserScheduleView.Course@' + this.model.toString();
};
