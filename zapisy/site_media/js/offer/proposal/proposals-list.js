/**
 * Kod odpowiedzialny za listę przedmiotów w systemie zapisów.
 */

ProposalsList = new Object();

/**
 * Inicjuje widok listy proposzycji.
 */
ProposalsList.init = function()
{
	ProposalsList.initProposalLists();
	ProposalsList.initFilter();
};

$(ProposalsList.init);

/**
 * Inicjuje listy przedmiotów
 */
ProposalsList.initProposalLists = function()
{
	ProposalsList.proposals = new Object();
        $('#proposal-list').find('ul.proposal-list')
                .children('li').
			each(function(i, proposalContainer)
		{
			proposalContainer = $(proposalContainer);
			var link = proposalContainer.children('a').assertOne();

			var proposal = new ProposalsList.Proposal();
			proposal.id = link.attr('id').removePrefix('proposal-').castToInt();
			proposal.name = link.text().trim();

			proposal.container   = proposalContainer;
            proposal.wasEnrolled = proposalContainer.children('input[name=wasEnrolled]').attr('value').castToBool();
            proposal.english     = proposalContainer.children('input[name=english]').attr('value').castToBool();
            proposal.type     = proposalContainer.children('input[name=type]').attr('value').castToInt(true);
            proposal.exam         = proposalContainer.children('input[name=exam]').attr('value').castToBool();
            proposal.teacher     = proposalContainer.children('input[name=teacher]').attr('value').castToInt(true);
            proposal.status      = proposalContainer.children('input[name=status]').attr('value').castToInt(true);
			ProposalsList.proposals[proposal.id] = proposal;
		});
};

/**
 * Inicjuje filtrowanie.
 */
ProposalsList.initFilter = function()
{

	var proposalFilterForm = $('#enr-proposalsList-top-bar').assertOne();

	proposalFilterForm.css('display', 'block');

	proposalFilterForm.find('.filter-phrase-reset').assertOne().click(function()
	{
		proposalFilterForm.find('.filter-phrase').assertOne().attr('value', '');
	});

	// komunikat o pustym filtrze
	ProposalsList.emptyFilterWarning =
		$.create('p', {className: 'main-side-message'}).
		text('Do podanego filtra nie pasuje żadna propozycja.').
		css({marginTop: '50px', display: 'none'}).
		insertAfter($('#proposal-list').assertOne());
	ProposalsList.emptyFilterWarningVisible = false;

	// konfiguracja filtra

	ProposalsList.proposalFilter = new ListFilter('proposalsList-proposals', proposalFilterForm.getDOM());
	
	ProposalsList.proposalFilter.afterFilter = function(matchedElementsCount)
	{
		var visible = (matchedElementsCount == 0);
		if (ProposalsList.emptyFilterWarningVisible == visible)
			return;
		ProposalsList.emptyFilterWarningVisible = visible;
		ProposalsList.emptyFilterWarning.css('display', visible?'':'none');
	};

	ProposalsList.proposalFilter.addFilter(ListFilter.CustomFilters.createSimpleTextFilter(
		'phrase', '.filter-phrase', function(element, value)
	{
		var proposal = element.data;
		return (proposal.name.toLowerCase().indexOf(value.toLowerCase()) >= 0);
	}));

    ProposalsList.proposalFilter.addFilter(ListFilter.CustomFilters.createCourseTypeFilter(
   		function(element, courseType)
   	{
   		var course = element.data;
   		return (course.type == courseType);
   	}));

    ProposalsList.proposalFilter.addFilter(ListFilter.CustomFilters.createSimpleComboFilter(
        'teacher', '#enr-teacher', function(element, value){

            if (!value || value == -1)
          			return true;
          		var course = element.data;
            return (course.teacher == value);
    }));
//
    ProposalsList.proposalFilter.addFilter(ListFilter.CustomFilters.createSimpleBooleanFilter(
   		'hideSigned', '#enr-hidesigned', function(element, value)
   	{
   		if (!value)
   			return true;
   		var course = element.data;
   		return !course.wasEnrolled;
   	}));

   	ProposalsList.proposalFilter.addFilter(ListFilter.CustomFilters.createSimpleBooleanFilter(
   		'showEnglish', '#enr-proposalFilter-english', function(element, value)
   	{
   		if(value)
   			return true;
   		var course = element.data;
   		return !course.english;
   	}));
   	ProposalsList.proposalFilter.addFilter(ListFilter.CustomFilters.createSimpleBooleanFilter(
   		'showExam', '#enr-proposalFilter-exam', function(element, value)
   	{
   		if(value)
   			return true;
   		var course = element.data;
   		return !course.exam;
   	}));

   	ProposalsList.proposalFilter.addFilter(ListFilter.CustomFilters.createSimpleBooleanFilter(
   		'vote', '#enr-proposalFilter-vote', function(element, value)
   	{

   		var course = element.data;
       if(!value){
                return course.status == 2;
       }
   		return true;
   	}));


	for (var proposal in ProposalsList.proposals)
	{
		proposal = ProposalsList.proposals[proposal];
		ProposalsList.proposalFilter.addElement(new ListFilter.Element(proposal, function(visible)
		{
			var proposal = this.data;
			proposal.setVisible(visible);
		}));
	};

	ProposalsList.proposalFilter.runThread();
	$('#enr-proposalsList-top-bar').find('label').disableDragging();
};



/*******************************************************************************
 * Klasa przedmiotu.
 ******************************************************************************/

/**
 * Konstruktor modelu przedmiotu.
 */
ProposalsList.Proposal = function()
{
    this.id = null;
   	this.name = null;
   	this.container = null;
   	this.visible = true;
   	this.type = null;
   	this.wasEnrolled = null; // czy aktualny student był zapisany
   	this.english = null;
   	this.exam = null;
    this.teacher = null;
    this.status  = null;
};

/**
 * Ustawia widoczność przedmiotu na liście.
 *
 * @param visible true, jeżeli przedmiot ma być widoczny
 */
ProposalsList.Proposal.prototype.setVisible = function(visible)
{
	if (visible == this.visible)
		return;
	this.visible = visible;

	this.container.css('display', visible?'':'none');
};
