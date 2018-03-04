/**
 * Model terminu przedmiotu, do operacji na danych.
 */

if (!Fereol.Enrollment)
	Fereol.Enrollment = new Object();

Fereol.Enrollment.CourseGroup = function()
{
	this.id = null;
	this.type = null;
	this.course = null;

	this.url = null;
	this.teacherName = null;
	this.teacherURL = null;

	this.isEnrolled = null; // czy student jest zapisany
	this.isQueued = null; // czy jest "w kolejce"
	this.isPinned = null; // czy przypiął do planu
	this.isTeacher = null; // czy jest prowadzącym daną grupę
	this.queuePriority = null; // jeżeli jest w kolejce, to jaki ma priorytet

	// w przypadku studentów nie zamawianych - zamawiana część grupy jest
	// "niedostępna"
	this.limit = null;
	this.unavailableLimit = null;
	this.enrolledCount = null;
	this.unavailableEnrolledCount = null;
	this.queuedCount = null;

	this.updateListeners = [];

	if (!Fereol.Enrollment.CourseGroup._setEnrolledURL)
		Fereol.Enrollment.CourseGroup._setEnrolledURL =
			$('input[name=ajax-set-enrolled-url]').assertOne().attr('value');
	if (!Fereol.Enrollment.CourseGroup._setPinnedURL)
		Fereol.Enrollment.CourseGroup._setPinnedURL =
			$('input[name=ajax-set-pinned-url]').assertOne().attr('value');
	if (!Fereol.Enrollment.CourseGroup._setQueuePriorityURL)
		Fereol.Enrollment.CourseGroup._setQueuePriorityURL =
			$('input[name=ajax-set-queue-priority-url]').assertOne().
				attr('value');
	if (!Fereol.Enrollment.CourseGroup._priorityLimit)
		Fereol.Enrollment.CourseGroup._priorityLimit =
			$('input[name=priority-limit]').assertOne().attr('value').
				castToInt();
};

Fereol.Enrollment.CourseGroup.groupTypes =
{
	1: ['wykład', 'wyk'],
	2: ['ćwiczenia', 'ćw'],
	3: ['pracownia', 'prac'],
	4: ['ćwiczenia (zaaw)', 'ćw-z'],
	5: ['ćwiczenia + prac.', 'ćw+prac'],
	6: ['seminarium', 'sem'],
	7: ['lektorat', 'lek'],
	8: ['wf', 'wf'],
    9: ['repetytorium', 'rep'],
   10: ['projekt', 'proj']
};

Fereol.Enrollment.CourseGroup._byID = {};

Fereol.Enrollment.CourseGroup.prototype._register = function()
{
	Fereol.Enrollment.CourseGroup._byID[this.id] = this;
};

Fereol.Enrollment.CourseGroup.getByID = function(id)
{
	if (!Fereol.Enrollment.CourseGroup._byID[id])
		throw new Error('Grupa nie istnieje');
	return Fereol.Enrollment.CourseGroup._byID[id];
};

Fereol.Enrollment.CourseGroup.prototype._notifyUpdateListeners = function()
{
	this.updateListeners.forEach(function(listener)
	{
		listener();
	});
};

Fereol.Enrollment.CourseGroup.fromJSON = function(json)
{
	var raw = json;
	if (typeof raw == 'string')
		raw = $.parseJSON(json);

	var ct = new Fereol.Enrollment.CourseGroup();

	ct.id = raw['id'].castToInt();
	ct.type = raw['type'].castToInt();
	ct.course = Fereol.Enrollment.Course.getByID(raw['course'].castToInt());

	ct.url = raw['url'];
	ct.teacherName = raw['teacher_name'];
	ct.teacherURL = raw['teacher_url'];
	if (!ct.teacherURL)
		ct.teacherURL = null;

	ct.updateFromJSON(json);

	ct._register();
	return ct;
};

Fereol.Enrollment.CourseGroup.prototype.updateFromJSON = function(json)
{
	var raw = json;
	if (typeof raw == 'string')
		raw = $.parseJSON(json);

	this.isEnrolled = !!raw['is_enrolled'];
	this.isQueued = !!raw['is_queued'];
	this.isPinned = !!raw['is_pinned'];
	this.isTeacher = !!raw['is_teacher'];

	this.limit = raw['limit'].castToInt();
	this.unavailableLimit = raw['unavailable_limit'].castToInt();
	this.enrolledCount = raw['enrolled_count'].castToInt();
	this.unavailableEnrolledCount = raw['unavailable_enrolled_count'].castToInt();
	this.queuedCount = raw['queued_count'].castToInt();
	if (this.isQueued)
		this.queuePriority = raw['queue_priority'].castToInt();
};

Fereol.Enrollment.CourseGroup.prototype.availableLimit = function()
{
	if (this.limit === null ||
		this.unavailableLimit === null)
		throw new Error('NullPointerException');
	return this.limit - this.unavailableLimit;
};

Fereol.Enrollment.CourseGroup.prototype.availableEnrolledCount = function()
{
	if (this.enrolledCount === null ||
		this.unavailableEnrolledCount === null)
		throw new Error('NullPointerException');
	return this.enrolledCount - this.unavailableEnrolledCount;
};

/**
 * @return true, jeżeli grupa jest pełna
 */
Fereol.Enrollment.CourseGroup.prototype.isFull = function()
{
	return this.availableLimit() <= this.availableEnrolledCount();
};

Fereol.Enrollment.CourseGroup.prototype.isEnrolledOrQueued = function()
{
	return this.isEnrolled || this.isQueued;
};

Fereol.Enrollment.CourseGroup.prototype.getTypeName = function(fullName)
{
	return Fereol.Enrollment.CourseGroup.groupTypes[this.type][fullName ? 0:1];
};

/******************************************************************************/

/**
 * Zapisuje lub wypisuje użytkownika do/z grupy lub kolejki (w zależności od
 * wolnych miejsc.
 *
 * @param enroll true, jeżeli zapisać; false aby wypisać
 */
Fereol.Enrollment.CourseGroup.prototype.setEnrolled = function(enroll)
{

    if( user_is_student ){
    if (!confirm("Czy na pewno chcesz to zrobić?"))
        return;
    }
	if (!Fereol.Enrollment.CourseGroup._setLoading(true))
		return;
	$.dataInvalidate();



	if (!this.course.isRecordingOpen)
		throw new Error('Zapisy na ten przedmiot są zamknięte');

	var self = this;
	enroll = !!enroll;
	//nie sprawdzamy if enroll == isEnrolled (bo jest jeszcze kolejka)
    if( user_is_student ){
	$.post(Fereol.Enrollment.CourseGroup._setEnrolledURL, {
		group: this.id,
		enroll: enroll
	}, function(data)
	{
		var result = AjaxMessage.fromJSON(data);

		if (result.isSuccess())
		{
			// do nothing special
		}
		else if (result.code == 'Queued' || result.code == 'AlreadyQueued')
			result.displayMessageBox();
		else
			result.displayMessageBox();

		if (result.data)
		{
			for (var gid in result.data)
				Fereol.Enrollment.CourseGroup.getByID(gid).
					updateFromJSON(result.data[gid]);
			for (var gid in result.data)
				Fereol.Enrollment.CourseGroup.getByID(gid).
					_notifyUpdateListeners();
		}
		
		Fereol.Enrollment.CourseGroup._setLoading(false);
	}, 'json');
    }
};

Fereol.Enrollment.CourseGroup.prototype.setPinned = function(pinned)
{
	if (!Fereol.Enrollment.CourseGroup._setLoading(true))
		return;
	$.dataInvalidate();

	var self = this;
	pinned = !!pinned;
	if (this.isPinned == pinned)
		return;
    if( user_is_student ){
	$.post(Fereol.Enrollment.CourseGroup._setPinnedURL, {
		group: this.id,
		pin: pinned
	}, function(data)
	{
		var result = AjaxMessage.fromJSON(data);
		if (result.isSuccess())
			self.isPinned = pinned;
		else
			result.displayMessageBox();

		self._notifyUpdateListeners();
		Fereol.Enrollment.CourseGroup._setLoading(false);
	}, 'json');
    } else {
        self.isPinned = pinned;
        self._notifyUpdateListeners();
        Fereol.Enrollment.CourseGroup._setLoading(false);
    }
};

/**
 * Zmienia priorytet grupy.
 *
 * @param newPriority nowy priorytet (1-10)
 */
Fereol.Enrollment.CourseGroup.prototype.changePriority = function(newPriority)
{
	if (!Fereol.Enrollment.CourseGroup._setLoading(true))
		return;

	var self = this;
	if (newPriority < 1 ||
		newPriority > Fereol.Enrollment.CourseGroup._priorityLimit)
		throw new Error('Nieprawidłowy priorytet do ustawienia');
	this.queuePriority = newPriority;

	$.dataInvalidate();
    if( user_is_student ){
	$.post(Fereol.Enrollment.CourseGroup._setQueuePriorityURL, {
			id: this.id,
			priority: newPriority
		}, function(data)
	{
		var result = AjaxMessage.fromJSON(data);
		if (result.isSuccess())
		{
			Fereol.Enrollment.CourseGroup._setLoading(false);
            self._notifyUpdateListeners();
		}
		else
			result.displayMessageBox();
	}, 'json');
    } else {
        Fereol.Enrollment.CourseGroup._setLoading(false);
         self._notifyUpdateListeners();
    }
};

/******************************************************************************/

Fereol.Enrollment.CourseGroup.prototype.toString = function()
{
	return 'CourseGroup#' + this.id;
}

/**
 * Włącza lub wyłącza tryb komunikacji z serwerem. W tym trybie może być tylko
 * jeden "wątek".
 *
 * @param loading true, jeżeli włączyć
 * @return true, jeżeli zakończono powodzeniem
 */
Fereol.Enrollment.CourseGroup._setLoading = function(loading)
{
	loading = !!loading;
	if (loading && Fereol.Enrollment.CourseGroup._isLoading)
		return false;
	Fereol.Enrollment.CourseGroup._isLoading = loading;
	Fereol.Enrollment.CourseGroup.loadingListeners.forEach(function(e)
	{
		e(loading);
	});
	return true;
};

Fereol.Enrollment.CourseGroup.loadingListeners = [];
