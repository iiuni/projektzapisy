/**
 * Model terminu przedmiotu, tzn zakresu godzinowego dla określonej grupy
 * z określonego przedmiotu, do wyświetlenia w prototypie planu lub terminarzu.
 */

if (!Fereol.Enrollment)
	Fereol.Enrollment = new Object();

Fereol.Enrollment.ScheduleCourseTerm = function()
{
	this.id = null;
	this.classroom = null;
	
	this.isPrototyped = false; // czy jest tymczasowo wyświetlony w prototypie
	this._isVisible = false;
	this.displayStyle =
		Fereol.Enrollment.ScheduleCourseTerm.DisplayStyle.SCHEDULE;

	this.group = null; // model danych
	this.scheduleTerm = null; // Schedule.Term
	this.schedule = null;

	this.container = $.create('div');
	this.popupContents = $.create('div');

	this._containerReady = false;
	this._controlsReady = false;
};

Fereol.Enrollment.ScheduleCourseTerm.DisplayStyle = {
	SCHEDULE: 1,
	PROTOTYPE: 2
};

Fereol.Enrollment.ScheduleCourseTerm._isLoading = false;

Fereol.Enrollment.ScheduleCourseTerm._byID = {};

Fereol.Enrollment.ScheduleCourseTerm.fromJSON = function(json, readOnly)
{
	let obj = $.parseJSON(json)
    return Fereol.Enrollment.ScheduleCourseTerm.fromObject(obj);
};

Fereol.Enrollment.ScheduleCourseTerm.fromObject = function(obj)
{
    var sterm = new Fereol.Enrollment.ScheduleCourseTerm();
    
    sterm.id = obj['id'].castToInt();
	sterm.group = Fereol.Enrollment.CourseGroup.getByID(obj['group'].castToInt());
	sterm.group.updateListeners.push(function()
	{
		sterm._updateVisibility();
		sterm._updateControls();
	});
    
    let startTimes = obj.start_time.split(":");
    let endTimes = obj.end_time.split(":");
    
	sterm.scheduleTerm = new Schedule.Term(
		obj.day.castToInt() - 1,
		new Schedule.Time(parseInt(startTimes[0]), parseInt(startTimes[1])),
		new Schedule.Time(parseInt(endTimes[0]), parseInt(endTimes[1])),
		sterm.container,
		sterm.popupContents
	);
	sterm.scheduleTerm.onResize = function(isFullSize)
	{
		sterm._onResize(isFullSize);
	};

	sterm.classroom = obj.classroom;

	Fereol.Enrollment.ScheduleCourseTerm._byID[sterm.id] = sterm;

	return sterm;
};

Fereol.Enrollment.ScheduleCourseTerm.prototype.assignSchedule = function(schedule)
{
	this.schedule = schedule;
	this._updateVisibility();
};

Fereol.Enrollment.ScheduleCourseTerm.prototype._updateVisibility = function()
{
	var self = this;

	if (!this._containerReady)
	{
		this._containerReady = true;

		$.create('span', {className: 'name'}).text(this.group.course.shortName).
			attr('title', this.group.course.name).appendTo(this.container);
		this._teacherLabel = $.create('span', {className: 'teacher'}).text(this.group.teacherName).
			appendTo(this.container);
		this._typeLabel = $.create('span', {className: 'type'}).
			appendTo(this.container).attr('title',
			this.group.getTypeName(true));

		if (this.classroom)
		{
			this._classroomLabel = $.create('span', {className: 'classroom'}).
				appendTo(this.container);
			this._classroomLabel.text('s. ' + this.classroom);
		}

		this._controlsBox = null;
		if (this.displayStyle ==
			Fereol.Enrollment.ScheduleCourseTerm.DisplayStyle.PROTOTYPE)
		{
			this._controlsBox = $.create('div', {className: 'controls'}).
				appendTo(this.container).css('display', 'none');

			this._pinUnpinButton = $.create('span', { className: 'pinUnpin'}).
				appendTo(this._controlsBox);
			this._signInOutButton = $.create('span', { className: 'signInOut'}).
				appendTo(this._controlsBox);
            
			this._loadingIndicator =
				$.create('div', { className: 'loadingIndicator'}).
				appendTo(this._controlsBox).css('display', 'none');

			this.container.mouseenter(function()
			{
				if (!self._controlsEmpty)
					self._controlsBox.css('display', 'block');
			}).mouseleave(function()
			{
				self._controlsBox.css('display', 'none');
			});
			this._controlsBox.click(function(ev)
			{
				ev.stopPropagation();
			});
		}

		this.container.click(function()
		{
			self._generatePopup();
			self.scheduleTerm.setPopupVisible(true);
		});
		this.popupContents.mouseleave(function()
		{
			self.scheduleTerm.setPopupVisible(false);
		});
	}
	this._updateControls();

	this.container.toggleClass('pinned', this.group.isPinned);
	this.container.toggleClass('enrolled', this.group.isEnrolled);
	this.container.toggleClass('queued', this.group.isQueued);
	this.container.toggleClass('full', this.group.isFull() &&
		!this.group.isEnrolledOrQueued());

	var shouldBeVisible = (this.group.isPinned || this.isPrototyped ||
		this.group.isEnrolledOrQueued() || this.group.isTeacher);
	if (this.displayStyle == Fereol.Enrollment.ScheduleCourseTerm.DisplayStyle.
		SCHEDULE)
		shouldBeVisible = true;
	if (shouldBeVisible == this._isVisible)
		return;
	this._isVisible = shouldBeVisible;
	if (shouldBeVisible)
		this.schedule.addTerm(this.scheduleTerm);
	else
	{
		this.schedule.removeTerm(this.scheduleTerm);
		if (this._controlsBox)
			this._controlsBox.css('display', 'none');
	}
};

Fereol.Enrollment.ScheduleCourseTerm.prototype._generatePopup = function()
{
	this.popupContents.empty();
	
	$.create('h2', {className: 'name'}).appendTo(this.popupContents).append(
		$.create('a').text(this.group.course.name).attr('href', this.group.course.url));
	$.create('p', {className: 'typeAndTerm'}).text(
		this.group.getTypeName(true).capitalize() +
		' (' + Schedule.dayNames[this.scheduleTerm.day].toLowerCase() + ' ' +
		this.scheduleTerm.timeFrom.toString() + '-' +
		this.scheduleTerm.timeTo.toString() + ')'
	).appendTo(this.popupContents);
    if (this.group.teacherURL)
	{
		$.create('p', {className: 'teacher'}).text('Prowadzący: ').
			appendTo(this.popupContents).append($.create('a').text(this.group.teacherName).
			attr('href', this.group.teacherURL));
    }
    else
	{
		$.create('p', {className: 'teacher'}).text('Prowadzący: ').
			appendTo(this.popupContents).append($.create('span').text(this.group.teacherName));
    }
	if (this.classroom)
		$.create('p', {className: 'classroom'}).text(
			'Sala: ' + this.classroom
		).appendTo(this.popupContents);

	if (this.displayStyle ==
		Fereol.Enrollment.ScheduleCourseTerm.DisplayStyle.PROTOTYPE)
	{
		var enrolled = $.create('p', {className: 'enrolledCount'}).
			text('Zapisanych: ').appendTo(this.popupContents);
		var groupLink = $.create('a', {
			href: this.group.url
		}).appendTo(enrolled);
		if (this.group.unavailableLimit)
		{
			groupLink.text(this.group.availableEnrolledCount() + '/' +
				this.group.availableLimit()).
				attr('title',
				'zapisanych osób w sumie: ' + this.group.enrolledCount +
				', limit miejsc w grupie: ' + this.group.limit +
				', zapisanych studentów zamawianych: ' +
					this.group.unavailableEnrolledCount +
				', miejsca gwarantowane dla studentów zamawianych: ' +
					this.group.unavailableLimit
			);
			$.createText(' + ' +
				this.group.unavailableEnrolledCount + '/' +
				this.group.unavailableLimit + ' stud. zamawianych').
				appendTo(enrolled);
		}
		else
			groupLink.text(this.group.enrolledCount + '/' + this.group.limit).
				attr('title', 'zapisanych osób: ' + this.group.enrolledCount +
				', limit miejsc w grupie: ' + this.group.limit);
		if (this.group.isFull() && !this.group.isEnrolledOrQueued())
			$.create('img', {
				src: '/static/images/warning.png',
				alt: '(brak wolnych miejsc)',
				title: 'nie ma wolnych miejsc w tej grupie, możesz zapisać ' +
					'się do kolejki'
			}).appendTo(enrolled.appendSpace());
		if (this.group.queuedCount > 0)
			$.create('span').text('(w kolejce: ' + this.group.queuedCount + ')').
				appendTo(enrolled.appendSpace());

		if (this.group.isEnrolledOrQueued())
		{
			var einfo = $.create('p', { className: 'enrolledInfo'}).
				appendTo(this.popupContents);
			if (this.group.isEnrolled)
				einfo.text('Jesteś zapisany do tej grupy.');
			if (this.group.isQueued)
				einfo.text('Jesteś w kolejce do tej grupy.');
		}
	}
	else if (this.displayStyle ==
		Fereol.Enrollment.ScheduleCourseTerm.DisplayStyle.SCHEDULE)
	{
		$.create('p', {className: 'groupListLink'}).appendTo(
			this.popupContents).append($.create('a', {
			href: this.group.url
		}).text('lista osób zapisanych do grupy'));
	}
};

Fereol.Enrollment.ScheduleCourseTerm.prototype._updateControls = function()
{
	var self = this;
	if (!this._controlsBox)
		return;
	
	if (!this._controlsReady)
	{
		this._controlsReady = true;

		this._signInOutButton.click(function()
		{
            if( user_is_student ){
                if (!confirm("Czy na pewno chcesz to zrobić?"))
                        return;
            }
			MessageBox.clear();
			self.group.setEnrolled(!self.group.isEnrolledOrQueued());
		});

		this._pinUnpinButton.click(function()
		{
            if( user_is_student ){
                if (!confirm("Czy na pewno chcesz to zrobić?"))
                        return;
            }
			MessageBox.clear();
			self.group.setPinned(!self.group.isPinned);
		});
	}
	this._controlsEmpty = false;

	if (Fereol.Enrollment.ScheduleCourseTerm._isLoading)
	{
		self._loadingIndicator.css('display', 'block');
		if (self._controlsBox)
			self._controlsBox.children('span').css('display', 'none');
		return;
	}
	self._loadingIndicator.css('display', 'none');

	this._pinUnpinButton.css({
		backgroundPosition: this.group.isPinned ? '-12px -12px' : '0 -12px',
		display: this.group.isEnrolledOrQueued() ? 'none' : ''
	}).attr('title', this.group.isPinned ? 'odepnij od planu' : 'przypnij do planu');
	
    // students are not allowed to leave the group 
    // (i.e. should not see the sign out button) if one of the following holds:
    // * recording is not open
    // * they're enrolled (not in queue) and leaving is not allowed (records ended)
    const displaySignInOutButton = 
        this.group.course.isRecordingOpen && 
        (!this.group.isEnrolled || Fereol.Enrollment.isLeavingAllowed);

	this._signInOutButton.css({
		backgroundPosition: this.group.isEnrolledOrQueued() ? '-12px 0' : '0 0',
		display: displaySignInOutButton ? '' : 'none'
	}).attr('title', this.group.isEnrolledOrQueued() ? 'wypisz się' +
		(this.group.isQueued ? ' z kolejki' : '') : 'zapisz się');
	
	this._controlsEmpty = this.group.isEnrolledOrQueued() &&
		!this.group.course.isRecordingOpen;
};

Fereol.Enrollment.ScheduleCourseTerm.prototype._onResize = function(isFullSize)
{
	var CLASSROOM_PADDING = 2;

	if (this.classroom)
		this._classroomLabel.css({
			left: (this._classroomLabel.parent().innerWidth() -
				CLASSROOM_PADDING * 2 -
				this._classroomLabel.width()) + 'px',
			top: (this._classroomLabel.parent().innerHeight() -
				this._classroomLabel.height() -
				CLASSROOM_PADDING) + 'px'
		});

	this._typeLabel.text(this.group.getTypeName(isFullSize)).css({
		top: (this._typeLabel.parent().innerHeight() -
			this._typeLabel.height() -
			CLASSROOM_PADDING) + 'px'
	});

	this._teacherLabel.css({
		display: isFullSize ? 'block' : 'none'
	});
};

Fereol.Enrollment.ScheduleCourseTerm.prototype.setPrototyped = function(prototyped)
{
	this.isPrototyped = prototyped;
	this._updateVisibility();
};

Fereol.Enrollment.ScheduleCourseTerm.prototype.toString = function()
{
	return this.group.course.name + ' - ' + this.scheduleTerm.toString();
};

Fereol.Enrollment.CourseGroup.loadingListeners.push(function(isLoading)
{
	Fereol.Enrollment.ScheduleCourseTerm._isLoading = isLoading;
	for (var id in Fereol.Enrollment.ScheduleCourseTerm._byID)
		Fereol.Enrollment.ScheduleCourseTerm._byID[id]._updateControls();
});
