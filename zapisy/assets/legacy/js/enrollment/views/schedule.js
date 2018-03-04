/**
 * Kod odpowiedzialny za plan zajęć.
 */

ScheduleView = new Object();

/**
 * Inicjuje widok planu.
 */

ScheduleView.init = function()
{
	ScheduleView.initGroups();

	var scheduleContainer = $('#enr-schedule-scheduleContainer').assertOne();

	ScheduleView.schedule = new Schedule(scheduleContainer, {
		dayColumnWidth: 170
	});

	ScheduleView.initCourseList();
};
$(ScheduleView.init);

ScheduleView.courseList = [];

ScheduleView.initGroups = function()
{
	var coursesRAW = $.parseJSON($(
		'#enr-schedule-scheduleContainer input[name=courses]').val());
	coursesRAW.forEach(function(courseRAW)
	{
		Fereol.Enrollment.Course.fromJSON(courseRAW);
	});

	var groupsRAW = $.parseJSON(
		$('#enr-schedule-scheduleContainer input[name=groups]').val());
	groupsRAW.forEach(function(groupRAW)
	{
		Fereol.Enrollment.CourseGroup.fromJSON(groupRAW);
	});
};

ScheduleView.initCourseList = function()
{
	var courseList = $('#enr-schedule-listByCourse');

	courseList.find('tr.courseDetails > td').each(function(idx, elem)
	{
		elem = $(elem);

		var course = new ScheduleView.Course();
		ScheduleView.courseList.push(course);

		course.model = Fereol.Enrollment.Course.getByID(
			elem.children('input[name=id]').attr('value').castToInt());

		course._listElementContainer = elem;

		elem.find('input[name=term]').each(function(idx, elem)
		{
			elem = $(elem);

			var sterm = Fereol.Enrollment.ScheduleCourseTerm.fromJSON(elem.attr('value'));
			sterm.displayStyle =
				Fereol.Enrollment.ScheduleCourseTerm.DisplayStyle.SCHEDULE;

			sterm.assignSchedule(ScheduleView.schedule);

			course.terms.push(sterm);
		});
	});
};

/*******************************************************************************
 * Klasa przedmiotu używanego w planie, tzn posiadającego kolekcję terminów.
 ******************************************************************************/

ScheduleView.Course = function()
{
	this.model = null; // model danych
	
	this.terms = [];
	this._listElementContainer = null;
	this._prototypedCheckbox = null;
};

ScheduleView.Course.prototype.toString = function()
{
	return 'ScheduleView.Course@' + this.model.toString();
};
