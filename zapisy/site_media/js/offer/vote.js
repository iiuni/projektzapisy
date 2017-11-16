/**
 * Funkcje i klasy odpowiedzialne za głosowanie studentów na ofertę dydaktyczną.
 *
 * @author Tomasz Wasilczyk (www.wasilczyk.pl)
 */

Vote = Object();

/**
 * Inicjuje formularz głosowania.
 */
Vote.init = function()
{
	// weryfikacja formularza (i tak potem jest to sprawdzane po stronie serwera)


	$('#od-vote-top-bar').find('label').disableDragging();

    $('.od-vote-course > select').change(function(){
        var el = $(this),
            li = $(this).parent();

        if( el.val() == 0 ){
            li.removeClass('changed').addClass('removed');
        } else {
            li.addClass('changed').removeClass('removed');
        }
    });



	Vote.initCounters();
//	Vote.initFilter();
};

$(Vote.init);
window.onunload = function(){ Vote.init(); $('.od-vote-course > select').trigger('change');  }
/**
 * Inicjuje liczniki punktów.
 */
Vote.initCounters = function()
{
    var sum = 0;
	// licznik punktów dla konkretnego semestru
	$('div.od-vote-semester').each(function(i, semesterNode)
	{
		var counterContainer = document.createElement('span');
		$(semesterNode).children('h2').append(counterContainer);
		counterContainer.appendChild(document.createTextNode(' (punktów: '));
		var counter = document.createElement('span');
		counterContainer.appendChild(counter);
		counterContainer.appendChild(document.createTextNode(')'));

		var votes = $(semesterNode).find('select');

		var countSemester = function()
		{
			var count = 0;
			for (var i = 0; i < votes.length; i++)
			{
                if (!( $(votes[i]).parent().find('.proposal-type-is_free').val() === 'True') ){

                    var voteValue = parseInt($.trim(votes[i].value));
                    if (isNaN(voteValue) || voteValue < 0)
                        throw new Error('Vote.refreshCounters: nieprawidłowa wartość głosu');
                    count += voteValue;
                }
			}

			$(counter).text(count);
		};
		countSemester();

		votes.change(countSemester);
	});

	// ogólne liczniki punktów
	var maxPointsNode = $('#od-vote-maxPoints');
	Vote.maxPoints = parseInt($.trim(maxPointsNode.children('span').text()));
	if (isNaN(Vote.maxPoints))
		throw new Error('Vote.init: Niepoprawna wartość maxPoints');

	maxPointsNode.empty();
	maxPointsNode = maxPointsNode[0];
	maxPointsNode.appendChild(document.createTextNode('Wykorzystane punkty w sumie: '));
	Vote.maxPointsNode = document.createElement('span');
	maxPointsNode.appendChild(Vote.maxPointsNode);
	maxPointsNode.appendChild(document.createTextNode('.'));

	Vote.totalCoursesCount = $('#od-vote-form').find('select').length;

	// włączenie liczników

	$('#od-vote-form').find('select').change(Vote.refreshCounters);

	Vote.refreshCounters();
};

/**
 * Odświeża liczniki w formularzu (wykorzystane punkty, przedmioty "na które
 * chce iść").
 */
Vote.refreshCounters = function()
{
	var votes = $('#od-vote-form').find('select');
	var totalPoints = 0;

	for (var i = 0; i < votes.length; i++)
	{
        if (!( $(votes[i]).parent().find('.proposal-type-is_free').val() === 'True') ){
		var voteValue = parseInt($.trim(votes[i].value));
		if (isNaN(voteValue) || voteValue < 0)
			throw new Error('Vote.refreshCounters: nieprawidłowa wartość głosu');
		totalPoints += voteValue;
        }
	}

	$(Vote.maxPointsNode).text(totalPoints + ' z ' + Vote.maxPoints);
	Vote.maxPointsNode.className = (totalPoints > Vote.maxPoints)?'warning':'';

	Vote.totalPoints = totalPoints;
};

/**
 * Inicjuje filtrowanie.
 */
Vote.initFilter = function()
{
	var courseFilterForm = $('#od-vote-top-bar').assertOne();

	courseFilterForm.css('display', 'block');

	courseFilterForm.find('.filter-phrase-reset').assertOne().click(function()
	{
		courseFilterForm.find('.filter-phrase').assertOne().attr('value', '');
	});

	// dodawanie do semestrów komunikatów o pustym filtrze
	var semesters = $('div.od-vote-semester');
	for (i = 0; i < semesters.length; i++)
	{
		var semester = semesters[i];

		var emptyFilterWarning = document.createElement('p');
		emptyFilterWarning.className = 'emptyFilterWarning';
		emptyFilterWarning.style.display = 'none';
		semester.appendChild(emptyFilterWarning);
		emptyFilterWarning.appendChild(document.createTextNode(
			'Do podanego filtra nie pasuje żaden przedmiot z tego semestru.'));
	}

	// konfiguracja filtra

	Vote.courseFilter = new ListFilter('vote-courses', courseFilterForm.getDOM());
	Vote.courseFilter.afterFilter = function()
	{
		var lists = $('#od-vote-form').find('ul');
		for (i = 0; i < lists.length; i++)
		{
			var visibleElements = $(lists[i]).children('li.visible');
			if (visibleElements.length == 0)
			{
				lists[i].style.display = 'none';
				$(lists[i].parentNode).children('.emptyFilterWarning')[0].style.display = 'block';
			}
			else
			{
				$(lists[i].parentNode).children('.emptyFilterWarning')[0].style.display = 'none';
				lists[i].style.display = '';
				for (var j = 0; j < visibleElements.length - 1; j++)
					visibleElements[j].style.borderBottomWidth = '1px';
				visibleElements[visibleElements.length - 1].style.borderBottomWidth = '0';
			}
		}
	};

	Vote.courseFilter.addFilter(ListFilter.CustomFilters.createSimpleTextFilter(
		'phrase', '.filter-phrase', function(element, value)
	{
		var course = $(element.data);
		return (course.children('label').text().toLowerCase().indexOf(value.toLowerCase()) >= 0);
	}));

	Vote.courseFilter.addFilter(ListFilter.CustomFilters.createSimpleBooleanFilter(
		'onlyWanted', '#od-vote-onlywanted', function(element, value)
	{
		if (!value)
			return true;
		var course = $(element.data);
		return course.hasClass('isFan');
	}));

	Vote.courseFilter.addFilter(ListFilter.CustomFilters.createCourseTypeFilter(
		function(element, courseType)
	{
		var course = $(element.data);
		return course.hasClass('course-type-' + courseType);
	}));

	var courses = $('#od-vote-form').find('li.od-vote-course');
	for (i = 0; i < courses.length; i++)
		Vote.courseFilter.addElement(new ListFilter.Element(courses[i], function(visible)
		{
			var course = $(this.data);
			if (visible)
				course.addClass('visible').removeClass('hidden');
			else
				course.removeClass('visible').addClass('hidden');
		}));

	Vote.courseFilter.runThread(true);
};
