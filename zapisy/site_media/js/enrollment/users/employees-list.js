/**
 * Kod odpowiedzialny za listę pracowników w systemie zapisów.
 */

EmployeesList = new Object();

/**
 * Inicjuje widok listy pracowników.
 */
EmployeesList.init = function()
{
	EmployeesList.initEmployeeLists();
	EmployeesList.initFilter();
	$('.employee-profile-link').live('click', function(event){
        event.preventDefault();
	    loadEmployeeProfile($(this).attr('href'));
    })
};
EmployeesList.activeStudentProfile = null;

function loadEmployeeProfile(profileUrl){
    if (EmployeesList.activeStudentProfile == profileUrl)
    	return;
    EmployeesList.activeStudentProfile = profileUrl;

    var $profileDiv = $('#employee-profile'),
    $loadingDiv = $('<div>&nbsp;</div>').addClass('content-loading');
    $profileDiv.append($loadingDiv);
	var $mainDiv = $('#main-content').assertOne();
    
    scrollUpToElementIfWindowBelow("#enr-EmployeesList-top-bar");
    
    $.ajax({
        type: "POST",
        dataType: "html",
        url: profileUrl,
        success: function(resp){
            $mainDiv.empty();
            $mainDiv.append($(resp));
        },
        complete: function(){
            $loadingDiv.remove();
            history.pushState({}, "Profil pracownika", profileUrl);
			UserScheduleView.init();
        }
    });


}

$(EmployeesList.init);


EmployeesList.ajax = new Object();

EmployeesList.ajax.init = function()
{
    EmployeesList.ajax.activeA =  $('#user-list-menu li a.active').assertOne();
    $('.ajax').click(function(){
	    $('#employees-list').addClass('content-loading');
        EmployeesList.ajax.getList($(this).attr('href'));

        $(EmployeesList.ajax.activeA).removeClass('active')
        EmployeesList.ajax.activeA = $(this)
        $(this).addClass('active');

        return false;
    });
    
}
$(EmployeesList.ajax.init)
EmployeesList.ajax.getList = function(link)
{
    $.ajax({
        type: "POST",
        url: link,
        async: false,
        dataType: 'json',
        data: '',
        success: function(data){ EmployeesList.ajax.parseList(data); },
        complete: function(){

        $('.main-side-message').remove()
	    EmployeesList.initEmployeeLists();
	    EmployeesList.initFilter();}

    });
    history.pushState({}, "Lista pracowników", link);
}

EmployeesList.ajax.parseList = function(data)
{
    $('#employees-list').removeClass('content-loading');
    var employee_list = $('#employees-list').assertOne().children('ul.employees');
    $(employee_list).children().remove();
    if ( data.data )
    {
        $.each(data.data, function(i, employee)
        {
            $.tmpl( "employee", employee).appendTo(employee_list);
        })

    }
}


/**
 * Inicjuje listy pracownikow
 */
EmployeesList.initEmployeeLists = function()
{
    EmployeesList.parseEmployee();
};

/**
 * Inicjuje filtrowanie.
 */
EmployeesList.initFilter = function()
{
	var employeeFilterForm = $('#enr-EmployeesList-top-bar').assertOne();

	employeeFilterForm.css('display', 'block');

	employeeFilterForm.find('.filter-phrase-reset').assertOne().click(function()
	{
		employeeFilterForm.find('.filter-phrase').assertOne().attr('value', '');
	});

	// komunikat o pustym filtrze
	EmployeesList.emptyFilterWarning =
		$.create('p', {className: 'main-side-message'}).
		text('Do podanego filtra nie pasuje żaden pracownik.').
		css({marginTop: '50px', display: 'none'}).
		insertAfter($('#employees-list').assertOne());
	EmployeesList.emptyFilterWarningVisible = false;

	// konfiguracja filtra

	EmployeesList.employeeFilter = new ListFilter('EmployeesList-employees', employeeFilterForm.getDOM());
	
	EmployeesList.employeeFilter.afterFilter = function(matchedElementsCount, matchedElements)
	{
        if (matchedElements.length == 1)
      		{
      			matchedElements[0].data.container.children('a').assertOne().trigger('click');
      		}

		var visible = (matchedElementsCount == 0);
		if (EmployeesList.emptyFilterWarningVisible == visible)
			return;
		EmployeesList.emptyFilterWarningVisible = visible;
		EmployeesList.emptyFilterWarning.css('display', visible?'':'none');
	};

	EmployeesList.employeeFilter.addFilter(ListFilter.CustomFilters.createSimpleTextFilter(
		'phrase', '.filter-phrase', function(element, value)
	{
		var employee = element.data;
		var name  = (employee.name.toLowerCase().indexOf(value.toLowerCase()) >= 0);
        var short_old = (employee.short_old.toLowerCase().indexOf(value.toLowerCase()) >= 0);
        var short_new = (employee.short_new.toLowerCase().indexOf(value.toLowerCase()) >= 0);
        var email = (employee.email.toLowerCase().indexOf(value.toLowerCase()) >= 0);

        return name || short_old || short_new || email;
	}));


    EmployeesList.runEmployees( EmployeesList.employeeFilter );

	EmployeesList.employeeFilter.runThread(true);
	$('#enr-EmployeesList-top-bar').find('label').disableDragging();
};

EmployeesList.parseEmployee = function()
{
    EmployeesList.employees = new Object();
    $('#employees-list').assertOne().children('ul.employees').
            children('li').
            each(function(i, employeeContainer)
    {
        employeeContainer = $(employeeContainer)

        var employee = new EmployeesList.employee();
        employee.id = employeeContainer.children('input[name=employee-id]').
                assertOne().attr('value').castToInt();
        employee.name = employeeContainer.children('a.employee-profile-link').assertOne().text();
        employee.email = employeeContainer.children('input[name=employee-email]').
                assertOne().attr('value');
        employee.short_old = employeeContainer.children('input[name=employee-short_old]').
                assertOne().attr('value');
        employee.short_new = employeeContainer.children('input[name=employee-short_new]').
                assertOne().attr('value');

        employee.container = employeeContainer;
        EmployeesList.employees[i] = employee;

    });
}

EmployeesList.runEmployees = function( filter )
{
    filter.clearElements();
    for (var employee in EmployeesList.employees)
    {
        employee = EmployeesList.employees[employee];
        filter.addElement(new ListFilter.Element(employee, function(visible)
        {
            var employee = this.data;
            employee.setVisible(visible);
        }));
    };
}

/*******************************************************************************
 * Klasa pracwonika
 ******************************************************************************/

/**
 * Konstruktor modelu employeea.
 */
EmployeesList.employee = function()
{
	this.id = null;
	this.name = null;
	this.email = null;
    this.short_old = null; // index
    this.short_new = null; // index
	this.container = null;
	this.visible = true;
};

/**
 * Ustawia widoczność przedmiotu na liście.
 *
 * @param visible true, jeżeli przedmiot ma być widoczny
 */
EmployeesList.employee.prototype.setVisible = function(visible)
{
	if (visible == this.visible)
		return;
	this.visible = visible;

	this.container.css('display', visible?'':'none');
};
