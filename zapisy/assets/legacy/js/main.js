/**
 * Plik dołączany razem z głównym szablonem.
 */

Fereol = new Object();

Fereol.init = function()
{
	$('.main-labelledSelect').change(function()
	{
		$(this).children('.label').remove();
	});

	Fereol.initSubsystemTypeSelector();
	Fereol.initCSRFTokenHandling();

    $('.close').live('click', function(event){
        event.preventDefault();
        $(this).parent().parent().hide('slow', function(){ $(this).remove(); });
    } )
};

$(Fereol.init);

/**
 * Obsługa CSRF Token
 */
Fereol.initCSRFTokenHandling = function()
{
	$('html').ajaxSend(function(event, xhr, settings)
	{
		if (settings.type.toLowerCase() == 'post')
			xhr.setRequestHeader('X-CSRFToken', $.cookies.get('csrftoken'));
	});
};

/*******************************************************************************
 * Zarządzanie podsystemami.
 ******************************************************************************/

/**
 * Obiekt podsystemu.
 */
Fereol.Subsystem = function(name, baseHref)
{
	this.name = name;
	this.baseHref = baseHref;
};

/**
 * Lista używanych podsystemów
 */
Fereol.Subsystems = {
	ENROLLMENT: new Fereol.Subsystem('System zapisów', '/courses/'),
	OFFER: new Fereol.Subsystem('Kształtowanie oferty dydaktycznej', '/proposal/'),
	GRADE: new Fereol.Subsystem('Ocena zajęć', '/grade/')
};

/**
 * Inicjuje listę wyboru podsystemu.
 */
Fereol.initSubsystemTypeSelector = function()
{
	var currentSubsystem = Fereol.getCurrentSubsystem();
	if (!currentSubsystem)
		return;

	var systemTypeBar = $('#main-systemTypeBar').assertOne();
	systemTypeBar.empty();
	var subsystemSelectorButton = $.create('span').
		text(currentSubsystem.name).
		appendTo(systemTypeBar);

	var subsystemList = $.create('ul').appendTo(systemTypeBar);

	var currentSubsystemElement = $.create('li', { className: 'current' }).
		text(currentSubsystem.name).appendTo(subsystemList);

	for (var id in Fereol.Subsystems)
	{
		var subsystem = Fereol.Subsystems[id];
		if (subsystem == currentSubsystem)
			continue;
		
		var subsystemElement = $.create('li').appendTo(subsystemList);
		$.create('a').text(subsystem.name).attr('href', subsystem.baseHref).
			appendTo(subsystemElement);
	}

	Fereol.subsystemSelectorVisible = false;

	subsystemSelectorButton.mouseenter(function()
	{
		if (Fereol.subsystemSelectorVisible)
			return;
		Fereol.subsystemSelectorVisible = true;
		subsystemList.css('display', 'block');
		subsystemSelectorButton.css('display', 'none');
	});

	subsystemList.mouseleave(function()
	{
		if (!Fereol.subsystemSelectorVisible)
			return;
		Fereol.subsystemSelectorVisible = false;
		subsystemList.css('display', 'none');
		subsystemSelectorButton.css('display', 'block');
	});
};

/**
 * Pobiera identyfikator bieżącego podsystemu.
 */
Fereol.getCurrentSubsystem = function()
{
	if (typeof Fereol.currentSubsystem != 'undefined')
		return Fereol.currentSubsystem;

	var systemTypeBar = $('#main-systemTypeBar');
	if (systemTypeBar.length == 0)
		return Fereol.currentSubsystem = null;

	var currentSystemName = systemTypeBar.assertOne().text().trim();
	var currentSystem = null;

	for (var id in Fereol.Subsystems)
	{
		var subsystem = Fereol.Subsystems[id];
		if (subsystem.name == currentSystemName)
		{
			currentSystem = subsystem;
			break;
		}
	}

	return Fereol.currentSubsystem = currentSystem;
};
