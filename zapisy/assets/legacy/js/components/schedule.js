/**
 * Komponent terminarza (widok tygodnia).
 */

Schedule = function(container, options)
{
	this.options =
	{
		hourColumnWidth: 45,
		dayColumnWidth: 125,
		hourHeight: 31,
		dayRowHeight: 25,
		bordersSize: 1,

		dayList: [0, 1, 2, 3, 4],

		startTime: new Schedule.Time(8, 00),
		endTime: new Schedule.Time(23, 00),

		hourLabelHeight: 12
	};
	if (options)
		this.options = $.extend(this.options, options);
	var o = this.options;

	this.terms = [];

	var i;

	this.container = container.assertOne();
	this.container.empty();
	this.container.attr('className', 'schedule');

	this.currentPopup = null;

	var minutesCount = o.endTime.timestamp - o.startTime.timestamp;
	var hoursCount = Math.ceil(minutesCount / 60);

	this.container.css({
		height: (
			(o.hourHeight + o.bordersSize) * hoursCount +
			o.dayRowHeight +
			2 * o.bordersSize +
			Math.round(o.hourLabelHeight / 2)) + 'px'
	});

	var termsContainerWidth =
		(o.dayColumnWidth + o.bordersSize) * o.dayList.length - o.bordersSize;
	var termsContainerHeight = //nie dokładnie liczone
		Math.ceil((o.hourHeight + o.bordersSize) * minutesCount / 60);

	this.termsContainer = $.create('div', {className: 'termsContainer'}).
		appendTo(this.container).css({
		top: o.dayRowHeight + 'px',
		left: o.hourColumnWidth + 'px',
		width: termsContainerWidth + 'px',
		height: termsContainerHeight + 'px'
	});

	this.rulesContainer = $.create('div', {className: 'rulesContainer'}).
		appendTo(this.termsContainer);

	this.termsSubcontainer = $.create('div', {className: 'termsSubcontainer'}).
		appendTo(this.termsContainer);

	this.hourLabelsContainer = $.create('div', {className: 'hourLabelsContainer'}).
		appendTo(this.container).css({
		top: o.dayRowHeight - Math.round(o.hourLabelHeight / 2) + 'px',
		width: o.hourColumnWidth + 'px',
		height: (termsContainerHeight + o.hourLabelHeight) + 'px'
	});

	this.dayLabelsContainer = $.create('div', {className: 'dayLabelsContainer'}).
		appendTo(this.container).css({
		left: (o.hourColumnWidth + o.bordersSize) + 'px',
		width: termsContainerWidth + 'px'
	});

	//generowanie kratek
	var rulePosition;
	for (i = 0; i < o.dayList.length; i++)
	{
		rulePosition = i * o.dayColumnWidth;
		if (i > 0)
			rulePosition += (i - 1) * o.bordersSize;

		$.create('div', {className: 'dayLabel'}).text(Schedule.dayNames[o.dayList[i]]).
			appendTo(this.dayLabelsContainer).css(
		{
			left: rulePosition + 'px',
			width: this.options.dayColumnWidth + 'px'
		});

		if (i == 0)
			continue;

		$.create('div', {className: 'dayRule'}).appendTo(this.rulesContainer).
			css(
		{
			left: rulePosition + 'px',
			height: termsContainerHeight + 'px'
		});
	}
	for (i = o.startTime; i.timestamp <= o.endTime.timestamp; i = i.nextFullHour())
	{
		var minuteOffset = i.timestamp - o.startTime.timestamp;
		var hoursBefore = Math.ceil(minuteOffset / 60);

		rulePosition = (hoursBefore - 1) * o.bordersSize +
			Math.ceil(minuteOffset * o.hourHeight / 60);

		var halfHourRuleTime = false;

		if (i.isFullHour())
		{
			$.create('span', {className: 'hourLabel'}).
				appendTo(this.hourLabelsContainer).text(i.toString()).css(
			{
				top: (rulePosition) + 'px'
			});

			if (i.timestamp + 30 < o.endTime.timestamp)
				halfHourRuleTime = i.timestamp + 30;
		}
		else
		{
			halfHourRuleTime = i.nextFullHour().timestamp - 30;
			if (halfHourRuleTime <= o.startTime.timestamp)
				halfHourRuleTime = false;
		}

		if (halfHourRuleTime)
		{
			halfHourRuleTime -= o.startTime.timestamp;
			var halfHourRulePosition = (hoursBefore - 1) * o.bordersSize +
				Math.ceil(halfHourRuleTime * o.hourHeight / 60);
			$.create('div', {className: 'halfHourRule'}).appendTo(this.rulesContainer).
				css(
			{
				top: halfHourRulePosition + 'px',
				width: termsContainerWidth + 'px'
			});
		}

		if (i.timestamp != o.startTime.timestamp &&
			i.timestamp != o.endTime.timestamp)
		{
			$.create('div', {className: 'hourRule'}).appendTo(this.rulesContainer).
				css(
			{
				top: rulePosition + 'px',
				width: termsContainerWidth + 'px'
			});
		}
	}
};

Schedule.dayNames = ['Poniedziałek', 'Wtorek', 'Środa', 'Czwartek', 'Piątek', 'Sobota', 'Niedziela'];

Schedule.prototype._timeToPosition = function(time, countLastBorder)
{
	var o = this.options;
	var position = Math.ceil(
		(time.timestamp - o.startTime.timestamp) * o.hourHeight / 60)

	var firstBorderAt = o.startTime.nextFullHour().timestamp;
	var lastBorderAt = time.nextFullHour().timestamp - 60;
	if (firstBorderAt <= lastBorderAt)
	{
		var bordersCount = Math.round((lastBorderAt - firstBorderAt) / 60) + 1;
		position += bordersCount * o.bordersSize;
	}

	if (!countLastBorder && lastBorderAt >= time.timestamp - 60 / o.hourHeight)
		position -= o.bordersSize;

	return position;
};

Schedule.prototype._dayToPosition = function(day)
{
	var o = this.options;
	var position = day * (o.dayColumnWidth + o.bordersSize);
	return position;
};

Schedule.prototype.addTerm = function(term)
{
	this.terms.push(term);
	this.termsSubcontainer.append(term.container);
	if (term._popupContainer)
		this.termsSubcontainer.append(term._popupContainer);
	term.schedule = this;
	term._invalidated = true;

	this.terms.forEach(function(aTerm)
	{
		term._anotherTermAdded(aTerm);
		aTerm._anotherTermAdded(term);
	});

	this._arrangeTerms();
};

Schedule.prototype.removeTerm = function(term)
{
	var idx = this.terms.indexOf(term);
	if (idx < 0)
		throw new Error('Termin nie jest w terminarzu');
	this.terms.remove(idx);
	term.container.detach();
	if (term._popupContainer)
		term._popupContainer.detach();

	this.terms.forEach(function(aTerm)
	{
		term._anotherTermRemoved(aTerm);
		aTerm._anotherTermRemoved(term);
	});

	this._arrangeTerms();
};

Schedule.prototype._arrangeTerms = function()
{
	var o = this.options;
	var i, j, k;
	var arrange = [];
	var collisionGroups = [];

	for (i = 0; i < this.terms.length; i++)
	{
		var pterm = this.terms[i];
		if (!pterm._invalidated)
			continue;
		if (arrange.indexOf(pterm) >= 0)
			continue;

		var ccol = pterm.getCoherentCollisions();
		collisionGroups.push(ccol);
		for (j = 0; j < ccol.length; j++)
		{
			var p2term = ccol[j];
			if (arrange.indexOf(p2term) >= 0)
				throw new Error('Ten podgraf nie powinien być jeszcze dodany');

			p2term._invalidated = true;
			arrange.push(p2term);
		}
	}

	for (i = 0; i < collisionGroups.length; i++)
	{
		var group = collisionGroups[i];
		var maxGroupWidth = 0;
		var currentGroupTerms = [];
		var term;

		for (j = 0; j < group.length; j++)
		{
			term = group[j];
			term._slot = -1;
			currentGroupTerms.push(term);
			currentGroupTerms = currentGroupTerms.sort(function(a, b)
			{
				return a.timeTo.timestamp - b.timeTo.timestamp;
			});
			var deleteAllBefore = term.timeFrom.timestamp;
			while (currentGroupTerms.length > 0 &&
				currentGroupTerms[0].timeTo.timestamp <= deleteAllBefore)
				currentGroupTerms.remove(0);
			if (maxGroupWidth < currentGroupTerms.length)
				maxGroupWidth = currentGroupTerms.length;
			var notAvailableSlots = {}
			for (k = 0; k < currentGroupTerms.length; k++)
				notAvailableSlots[currentGroupTerms[k]._slot] = true;
			var slotFound = false;
			for (k = 0; k < maxGroupWidth; k++)
				if (!notAvailableSlots[k])
				{
					slotFound = true;
					term._slot = k;
					break;
				}
			if (!slotFound)
				throw new Error('Nie znaleziono slotu');
		}

		for (j = 0; j < group.length; j++)
		{
			term = group[j];
			term._invalidated = false;

			var termPositionTop = this._timeToPosition(term.timeFrom, true);
			var termPositionHeight = this._timeToPosition(term.timeTo, false) - termPositionTop;
			var termWidth = Math.floor(
				(o.dayColumnWidth - (maxGroupWidth - 1) * o.bordersSize)
				/ maxGroupWidth);
			var termPositionLeftLocal =
				(termWidth + o.bordersSize) * term._slot;
			var termPositionLeft = this._dayToPosition(term.day) +
				termPositionLeftLocal;
			if (term._slot == maxGroupWidth - 1)
				termWidth += o.dayColumnWidth - termWidth - termPositionLeftLocal;

			term.container.css({
				position: 'absolute',
				width: termWidth + 'px',
				height: termPositionHeight + 'px',
				top: (termPositionTop - o.bordersSize) + 'px',
				left: (termPositionLeft - o.bordersSize) + 'px'
			});
			term.onResize(maxGroupWidth == 1);
		}
	}
};

/*******************************************************************************
 * Klasa Schedule.Time.
 ******************************************************************************/

Schedule.Time = function(hour, minute)
{
	this.timestamp = hour * 60 + minute;
};

Schedule.Time.prototype.isFullHour = function()
{
	return (this.timestamp % 60 == 0);
};

Schedule.Time.prototype.nextFullHour = function()
{
	var next;
	if (this.isFullHour())
		next = this.timestamp + 60;
	else
		next = Math.ceil(this.timestamp / 60) * 60;

	var time = new Schedule.Time();
	time.timestamp = next;
	return time;
};

Schedule.Time.prototype.toString = function()
{
	var hour = Math.floor(this.timestamp / 60);
	var minute = this.timestamp % 60;

	return hour + ':' + String(minute).lpad('0', 2);
};

/*******************************************************************************
 * Klasa Schedule.Term.
 ******************************************************************************/

Schedule.Term = function(day, timeFrom, timeTo, container, popupContents)
{
	this.day = day;
	this.timeFrom = timeFrom;
	this.timeTo = timeTo;
	this.schedule = null;
	this._invalidated = true;
	this._collisions = [];
	this.onResize = function(isFullSize) {};

	this.container = container.assertOne().addClass('term');

	this.popupVisible = false;
	this.popupContents = null;
	this._popupContainer = null;
	if (popupContents)
	{
		this._popupContainer = $.create('div',
			{className: 'termPopupContainer'}).toggle(false);
		this.popupContents = popupContents.assertOne().
			addClass('termPopupContents').appendTo(this._popupContainer);
		this.container.addClass('termWithPopup');
	}
};

Schedule.Term.prototype.collides = function(term)
{
	if (term.day != this.day)
		return false;

	var aFrom = this.timeFrom.timestamp;
	var bFrom = term.timeFrom.timestamp;
	var aTo = this.timeTo.timestamp;
	var bTo = term.timeTo.timestamp;

	return (
		(aFrom <= bFrom && bFrom < aTo) ||
		(bFrom <= aFrom && aFrom < bTo)
	);
};

Schedule.Term.prototype._anotherTermAdded = function(term)
{
	if (term == this)
		return;
	if (this._collisions.indexOf(term) >= 0)
		throw new Error('Już koliduje');
	if (this.collides(term))
	{
		this._invalidated = true;
		this._collisions.push(term);
	}
};

Schedule.Term.prototype._anotherTermRemoved = function(term)
{
	if (term == this)
		return;
	var idx = this._collisions.indexOf(term);
	if (idx >= 0)
	{
		this._invalidated = true;
		this._collisions.remove(idx);
	}
};

Schedule.Term.prototype.getCoherentCollisions = function()
{
	var collisions = [];

	var collisionsPush = function(term)
	{
		if (collisions.indexOf(term) >= 0)
			return;
		
		collisions.push(term);
		term._collisions.forEach(collisionsPush);
	};

	collisionsPush(this);

	return collisions.sort(function(a, b)
	{
		return a.timeFrom.timestamp - b.timeFrom.timestamp;
	});
};

Schedule.Term.prototype.setPopupVisible = function(visible)
{
	var self = this;
	this._popupContainer.stop();
	this.popupContents.stop();
	if (visible)
	{
		if (this.schedule.currentPopup !== this)
		{
			if (this.schedule.currentPopup)
				this.schedule.currentPopup.setPopupVisible(false);
			this.schedule.currentPopup = this;
		}
		this._popupContainer.css('opacity', 0);
		this._popupContainer.toggle(true);
		var contentsWidth = this.popupContents.outerWidth();
		var contentsHeight = this.popupContents.outerHeight();
		var termWidth = this.container.width();
		var termHeight = this.container.height();
		var termPosition = this.container.position();
		var dstPosLeft = Math.round(termPosition.left + termWidth / 2 -
			contentsWidth / 2);
		var dstPosTop = Math.round(termPosition.top + termHeight / 2 -
			contentsHeight / 2);
		var origContOffsetLeft = Math.round((termWidth - contentsWidth)/2);
		var origContOffsetTop = Math.round((termHeight - contentsHeight)/2);
		var scheduleWidth =  this.schedule.termsContainer.innerWidth();
		var scheduleHeight =  this.schedule.termsContainer.innerHeight();
		if (dstPosLeft + contentsWidth > scheduleWidth)
		{
			var newDstPosLeft = scheduleWidth - contentsWidth - 1;
			origContOffsetLeft += newDstPosLeft - dstPosLeft;
			dstPosLeft = newDstPosLeft;
		}
		if (dstPosLeft < 0)
		{
			dstPosLeft = -1;
			origContOffsetLeft = dstPosLeft - termPosition.left;
		}
		if (dstPosTop + contentsHeight > scheduleHeight)
		{
			var newDstPosTop = scheduleHeight - contentsHeight - 1;
			origContOffsetTop += newDstPosTop - dstPosTop;
			dstPosTop = newDstPosTop;
		}
		if (dstPosTop < 0)
		{
			dstPosTop = -1;
			origContOffsetTop = dstPosTop - termPosition.top;
		}

		this._popupContainer.css({
			left: termPosition.left + 'px',
			top: termPosition.top + 'px',
			width: termWidth + 'px',
			height: termHeight + 'px'
		});
		this.popupContents.css({
			left: origContOffsetLeft + 'px',
			top: origContOffsetTop + 'px'
		});

		this._popupContainer.animate({
			top: dstPosTop + 'px',
			left: dstPosLeft + 'px',
			width: contentsWidth + 'px',
			height: contentsHeight + 'px',
			opacity: 1
		}, {
			duration: 400,
			step: function(now, fx)
			{
				if (fx.prop == 'top')
					self.popupContents.css('top', (dstPosTop - now) + 'px');
				if (fx.prop == 'left')
					self.popupContents.css('left', (dstPosLeft - now) + 'px');
			}
		});
	}
	else
	{
		if (this.schedule.currentPopup === this)
			this.schedule.currentPopup = null;
		this._popupContainer.animate({
			opacity: 0
		}, 300, function()
		{
			self._popupContainer.toggle(false);
		});
	}
};

Schedule.Term.prototype.toString = function()
{
	return Schedule.dayNames[this.day] + ' ' +
		this.timeFrom.toString() + '-' +
		this.timeTo.toString();
};
