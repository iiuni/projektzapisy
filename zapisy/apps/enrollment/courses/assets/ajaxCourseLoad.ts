// Code to load course info asynchronously, without refreshing the page
// This script mutates the DOM to display the downloaded
// course info (TODO Vueify this). As such it depends on the
// layout of the DOM as defined in:
// -> templates/enrollment/courses/course.html
// -> templates/enrollment/courses/course_list.html
// -> template/base.html
// The received HTML response is then simply dumped into the DOM
// (main-content); we also update the page title and links

import * as $ from "jquery";
import { scrollUpToElementIfWindowBelow } from "common/utils";

let isLoadingCourse: boolean = false;
type CourseInfo = {
	courseName: string,
	courseHtml: string,
};

function installClickHandlers(): void {
	const links = document.querySelectorAll(".course-link");
	links.forEach(function(linkElem) {
		linkElem.addEventListener("click", onCourseLinkClicked);
	});
}

// When the user clicks on a course in the course list,
// send an async request to fetch course info
function onCourseLinkClicked(event: Event): void {
	event.preventDefault();
	if (isLoadingCourse) {
		return;
	}
	const clickedLink = event.target as HTMLHRElement;
	const courseUrl = clickedLink.getAttribute("href");
	if (!courseUrl) {
		throw new Error("Missing course link on event sender");
	}
	fetchCourseInfoAsync(courseUrl);
}

// Dispatch an AJAX GET request to the course
// page URL; the received response will be loaded
// into the DOM
function fetchCourseInfoAsync(courseUrl: string): void {

	isLoadingCourse = true;
	const container = document.getElementById("main-content");
	if (!container) {
		throw new Error("Missing container element");
	}
	setElementLoadingUi(container);
	scrollUpToElementIfWindowBelow("#main-menu-list");
	$.ajax({
		cache: false,
		type: "GET",
		dataType: "html",
		url: courseUrl + ".json",
		success: function(resp: string) {
			onCourseResponseReceived(resp, courseUrl);
		},
		error: function() {
			removeElementLoadingUi(container);
			alert("Nie udało się pobrać strony tego przedmiotu.");
		},
		complete: function() {
			isLoadingCourse = false;
		}
	});
}

// Add the "loading" spinner overlay
function setElementLoadingUi(elem: HTMLElement): void {
	const coveringLoadElem = document.createElement("div");
	coveringLoadElem.innerHTML = "&nbsp";
	coveringLoadElem.classList.add("content-loading");
	elem.appendChild(coveringLoadElem);
}

function removeElementLoadingUi(elem: HTMLElement): void {
	const elemChildren = Array.from(elem.children);
	elemChildren.forEach(function(child: Element) {
		const childClasses = Array.from(child.classList);
		if (childClasses.indexOf("content-loading") !== -1) {
			elem.removeChild(child);
		}
	});
}

function fillCourseHtml(courseHtml: string) {
	const mainContainer = document.getElementById("main-content");
	if (!mainContainer) {
		throw new Error("Missing main container element");
	}
	mainContainer.innerHTML = "";

	const courseContainer = document.createElement("div");
	if (!courseContainer) {
		throw new Error("Missing course container element");
	}
	courseContainer.setAttribute("id", "enr-course-view");
	courseContainer.innerHTML = courseHtml;
	mainContainer.appendChild(courseContainer);
}

function setPageTitle(courseName: string) {
	document.title = `${courseName} - System Zapisów`;
}

// At the top of the page we have the course name and
// if we're staff a link to the admin panel edit page
// on the right; they both need to be updated
function updateCourseNameAndEditLink(courseInfo: CourseInfo) {
	// The little arrow before the course name above the filters
	const courseNameElem = document.getElementById("enr-course-name");
	if (courseNameElem) {
		courseNameElem.innerText = courseInfo.courseName;
		courseNameElem.classList.remove("hidden");
	}
}

function pushHistoryEntry(url: string, thisCourseInfo: CourseInfo) {
	window.history.pushState(thisCourseInfo, "", url);
}

function onPopState(event: PopStateEvent) {
	if (event.state) {
		populateCoursePageFromCourseInfo(event.state);
	} else {
		// See https://stackoverflow.com/questions/2405117/difference-between-window-location-href-window-location-href-and-window-location
		window.location.href = window.location.href;
	}
}

function onCourseResponseReceived(resp: string, courseUrl: string) {
	const courseInfo: CourseInfo = JSON.parse(resp);
	pushHistoryEntry(courseUrl, courseInfo);
	populateCoursePageFromCourseInfo(courseInfo);
}

function populateCoursePageFromCourseInfo(courseInfo: CourseInfo) {
	fillCourseHtml(courseInfo.courseHtml);
	setPageTitle(courseInfo.courseName);
	updateCourseNameAndEditLink(courseInfo);
}

// The courses list itself is loaded with AJAX
// and when that happpens new HTMLHRElements are created
// so we need to reinstall our click handlers
// This event is emitted in CoursesList.js (in legacy assets)
document.addEventListener("CoursesListChanged", installClickHandlers);
window.addEventListener("popstate", onPopState);
