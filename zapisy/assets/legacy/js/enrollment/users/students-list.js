/**
 * Kod odpowiedzialny za listę studentów w systemie zapisów.
 */

StudentsList = new Object();

/**
 * Inicjuje widok listy studentów.
 */
StudentsList.init = function()
{
    $('.student-profile-link').live('click',function(event){
           event.preventDefault();
   	    loadStudentProfile($(this).attr('href'));
       });
	StudentsList.initStudentLists();
	StudentsList.initFilter();
};

StudentsList.activeStudentProfile = null;

function loadStudentProfile(profileUrl){
	if (StudentsList.activeStudentProfile == profileUrl)
		return;
	StudentsList.activeStudentProfile = profileUrl;

    var $profileDiv = $('#student-profile'),
    $loadingDiv = $('<div>&nbsp;</div>').addClass('content-loading');
    $profileDiv.append($loadingDiv);
    
    scrollUpToElementIfWindowBelow("#enr-StudentsList-top-bar");

    $.ajax({
        type: "POST",
        dataType: "html",
        url: profileUrl,
        success: function(resp){
            $profileDiv.empty();
            $profileDiv.append($(resp));
        },
        complete: function(){
            $loadingDiv.remove();
            history.pushState({}, "Profil pracownika", profileUrl);
			UserScheduleView.init();
        }
    });

}

$(StudentsList.init);

/*
 * Inicuje obsluge ajaxa
 */


StudentsList.ajax = new Object();

StudentsList.ajax.init = function()
{

    StudentsList.ajax.activeA =  $('#user-list-menu li a.active').assertOne();
    $('.ajax').click(function(){
	    $('#students-list').addClass('content-loading');
        StudentsList.ajax.getList($(this).attr('href'));

        $(StudentsList.ajax.activeA).removeClass('active')
        StudentsList.ajax.activeA = $(this)
        $(this).addClass('active');

        return false;
    });
}
$(StudentsList.ajax.init)
StudentsList.ajax.getList = function(link)
{
    $.ajax({
        type: "POST",
        url: link,
        async: false,
        dataType: 'json',
        data: '',
        success: StudentsList.ajax.parseList,
        complete: function() { history.pushState({}, "Profil pracownika", link); }
    });

}

StudentsList.ajax.parseList = function(data)
{
    $('#students-list').removeClass('content-loading');
    var student_list = $('#students-list').assertOne().children('ul.students');
    $(student_list).children().remove();
    StudentsList.studentFilter.clearElements();
    if ( data.data )
    {
        $.each(data.data, function(i, student)
        {
            $.tmpl( "student", student).appendTo(student_list);
        })
    }
    StudentsList.parseStudent();
    StudentsList.runStudents( StudentsList.studentFilter );
    StudentsList.studentFilter.doFilter()
}


/**
 * Inicjuje listy studentow
 */
StudentsList.initStudentLists = function()
{
    StudentsList.parseStudent();
};

/**
 * Inicjuje filtrowanie.
 */
StudentsList.initFilter = function()
{
	var studentFilterForm = $('#enr-StudentsList-top-bar').assertOne();

	studentFilterForm.css('display', 'block');

	studentFilterForm.find('.filter-phrase-reset').assertOne().click(function()
	{
		studentFilterForm.find('.filter-phrase').assertOne().attr('value', '');
	});

	// komunikat o pustym filtrze
	StudentsList.emptyFilterWarning =
		$.create('p', {className: 'main-side-message'}).
		text('Do podanego filtra nie pasuje żaden student.').
		css({marginTop: '50px', display: 'none'}).
		insertAfter($('#students-list').assertOne());
	StudentsList.emptyFilterWarningVisible = false;

	// konfiguracja filtra

	StudentsList.studentFilter = new ListFilter('StudentsList-students', studentFilterForm.getDOM());
	
	StudentsList.studentFilter.afterFilter = function(matchedElementsCount, matchedElements)
	{
		if (matchedElements.length == 1)
		{
			matchedElements[0].data.container.children('a').assertOne().trigger('click');
		}
		var visible = (matchedElementsCount == 0);
		if (StudentsList.emptyFilterWarningVisible == visible)
			return;
		StudentsList.emptyFilterWarningVisible = visible;
		StudentsList.emptyFilterWarning.css('display', visible?'':'none');

	};

	StudentsList.studentFilter.addFilter(ListFilter.CustomFilters.createSimpleTextFilter(
		'phrase', '.filter-phrase', function(element, value)
	{
		var student = element.data;
		var name  = (student.name.toLowerCase().indexOf(value.toLowerCase()) >= 0);
        var album = (student.album.toLowerCase().indexOf(value.toLowerCase()) >= 0);
        var email = (student.email.toLowerCase().indexOf(value.toLowerCase()) >= 0);

        return name || album || email;
	}));


    StudentsList.runStudents( StudentsList.studentFilter );

	StudentsList.studentFilter.runThread(true);
	$('#enr-StudentsList-top-bar').find('label').disableDragging();
};

StudentsList.parseStudent = function()
{
    StudentsList.students = new Object();
    $('#students-list').assertOne().children('ul.students').
            children('li').
            each(function(i, studentContainer)
    {
        studentContainer = $(studentContainer)

        var student = new StudentsList.student();

        student.id = studentContainer.children('input[name=student-user-id]').
                assertOne().attr('value').castToInt();
        student.name = studentContainer.children('a.student-profile-link').assertOne().text();
        student.email = studentContainer.children('input[name=student-email]').
                assertOne().attr('value');
        student.album = studentContainer.children('input[name=student-album]').
                assertOne().attr('value');


        student.container = studentContainer;

        StudentsList.students[student.id] = student;

    });
}

StudentsList.runStudents = function( filter )
{
    filter.clearElements();
    for (var student in StudentsList.students)
    {
        student = StudentsList.students[student];
        filter.addElement(new ListFilter.Element(student, function(visible)
        {
            var student = this.data;
            student.setVisible(visible);
        }));
    };

}

/*******************************************************************************
 * Klasa studenta.
 ******************************************************************************/

/**
 * Konstruktor modelu studenta.
 */
StudentsList.student = function()
{
	this.id = null;
	this.name = null;
	this.email = null;
    this.album = null; // index
	this.container = null;
	this.visible = true;
};

/**
 * Ustawia widoczność przedmiotu na liście.
 *
 * @param visible true, jeżeli przedmiot ma być widoczny
 */
StudentsList.student.prototype.setVisible = function(visible)
{
	if (visible == this.visible)
		return;
	this.visible = visible;

	this.container.css('display', visible?'':'none');
};
