/*
 * Client-side implementation of the course list,
 * using the FilteredCoursesList base class.
*/

"use strict";

function CoursesList()
{
    FilteredCoursesList.call(this);
};

CoursesList.prototype = Object.create(FilteredCoursesList.prototype);

CoursesList.prototype.init = function()
{
    FilteredCoursesList.prototype.init.call(this);
    
    let self = this;
    // The semester selector
    $("#enr-courseFilter-semester").change(function()
    {
        self.onNewSemesterChosen();
    });
    
    this.initCourseLists();
};

CoursesList.prototype.initCourseLists = function()
{
    const coursesListObject = FilteredCoursesList.getCoursesListFromJson();
    
    this.courses = coursesListObject.courseList;
    this.currentSemester = coursesListObject.semesterInfo;
    
    this.setCoursesFromData();
};

const listChangedEvent = new Event("CoursesListChanged");
CoursesList.prototype.setCoursesFromData = function()
{
    // Using this.courses and this.currentSemester, update the UI;
    // add courses from the current list to the HTML <ul> list, 
    // update the semester caption, etc.
    
    let self = this;
    this.courses.forEach(function(course)
    {
        self.addNewCourse(course);
    });

    // Let the ajax course list code know the list changed
    document.dispatchEvent(listChangedEvent);
    
    $("#current_semester_year").text(this.currentSemester.year);
    $("#current_semester_type").text(this.currentSemester.type);
    
    this.initFilters();
};

CoursesList.prototype.onNewSemesterChosen = function()
{
    // When a new semester is chosen, we make an AJAX request for the data.
    let newId = parseInt($("#enr-courseFilter-semester").find(":selected").val());
    this.userChosenSemester = newId;
    
    this.setDownloadingDataUi();
    
    let self = this;
    $.get(
        "/courses/get_semester_info/" + newId,
        function(d, s) { self.onSemesterInfoReceived(d, s); })
        .fail(function() { self.onSemesterInfoReceiveFailed(); });
};

CoursesList.prototype.onSemesterInfoReceiveFailed = function()
{
    // If we didn't succeed, restore the old UI and
    // show an error message box.
    this.setCoursesViewUi();
    
    $("#enr-courseFilter-semester").val(this.currentSemester.id);
    this.userChosenSemester = this.currentSemester.id;
    
    alert("Nie udało się pobrać listy przedmiotów dla tego semestru.");
};

CoursesList.prototype.onSemesterInfoReceived = function(data, status)
{
    // Otherwise save the data we received in response, clear the UI,
    // and re-set it from the new data.
    this.courses = data.courseList;
    this.currentSemester = data.semesterInfo;
    
    $("#courses-list").empty();
    this.setCoursesFromData();
    this.setCoursesViewUi();
};


CoursesList.prototype.setDownloadingDataUi = function()
{
    // Hide the current course list, show a notification
    // that lets the user know we're downloading data.
    
    $("#mainCoursesContainer").addClass("hidden");
    $("#fetchingListMessage").removeClass("hidden");
};

CoursesList.prototype.setCoursesViewUi = function()
{
    // The other way round - hide the notification,
    // show the course list.
    
    $("#mainCoursesContainer").removeClass("hidden");
    $("#fetchingListMessage").addClass("hidden");
};

CoursesList.prototype.addNewCourse = function(course)
{
    // Construct a HTML node (i.e. a link inside a <li>)
    // to be added to the HTML course list.
    // We also need to save the newly created <li> element
    // so the filter code in FilteredCoursesList can hide it
    // (or show it).
    
    let courseLink = $("<a/>", {
             "href" : course.url,
             "text" : course.name,
             "class" : "course-link"
        });
    course["htmlNode"] = $("<li/>");
    courseLink.appendTo(course["htmlNode"]);
    course["htmlNode"].appendTo($("#courses-list"));
};


$(document).ready(function()
{
    new CoursesList();
});
