/**
 * Klasa (statyczna) sidebara.
 */

Sidebar = {
	/**
	 * Czy sidebar jest widoczny.
	 */
	visible: null,

	/**
	 * Czy sidebar jest po prawej (false, jeżeli po lewej).
	 */
	isRightSidebar: null,

	/**
	 * Czy sidebar jest ukrywalny
	 */
	isDetachable: true
};

/**
 * Inicjowanie sidebara.
 */
Sidebar.init = function()
{
	var sidebarContainer = $('#main-sidebar');
	if (sidebarContainer.length != 1)
		return;

	// lista obserwatorów sidebara
	Sidebar._observers = new Array();

	Sidebar._sidebarContainer = sidebarContainer;
	Sidebar._mainContentContainer = $('#main-content-container').assertOne();
	Sidebar._mainContent = $('#main-content').assertOne();

	// ustalenie, czy jest po prawej, czy po lewej
	if (Sidebar._mainContentContainer.hasClass('sidebar-right') ==
		Sidebar._mainContentContainer.hasClass('sidebar-left'))
		throw 'Błąd: _mainContentContainer powinien mieć dokładnie jedną z' +
			'klas: sidebar-right, sidebar-left';
	Sidebar.isRightSidebar = Sidebar._mainContentContainer.
		hasClass('sidebar-right');
	Sidebar.isDetachable = !Sidebar._mainContentContainer.hasClass('sidebar-non-detachable');
/*
	if (Sidebar.isDetachable)
	{
		// akcja chowania lub ukrywania sidebara
		var toggleVisibility = function()
		{
			Sidebar.setVisible(!Sidebar.visible);
		};

		// generowanie przycisków ukrywania i pokazywania sidebara

		Sidebar._hideButton = $.create('a',
			{ className: 'main-sidebar-toggle-button hide' }).
			appendTo(Sidebar._sidebarContainer).text(Sidebar.isRightSidebar?'>':'<').
			disableDragging().click(toggleVisibility);
		Sidebar._showButton = $.create('a',
			{ className: 'main-sidebar-toggle-button show' }).
			prependTo($(Sidebar._mainContent)).text(Sidebar.isRightSidebar?'<':'>').
			disableDragging().click(toggleVisibility);


	}
*/
	// ustalenie widoczności sidebara na podstawie cookie, lub (jeżeli
	// niedostępne) kodu html (czy główny kontener ma klasę sidebar-visible)
	var cookieStatus = $.cookies.get('sidebar-visible');
	if (cookieStatus !== null)
		Sidebar.setVisible(cookieStatus);
	else
		Sidebar.setVisible(Sidebar._mainContentContainer.
			hasClass('sidebar-visible'));
};

$(Sidebar.init);

/**
 * Pokazuje, lub ukrywa sidebar.
 *
 * @param visible true, jeżeli sidebar ma zostać pokazany; false w p. p.
 */
Sidebar.setVisible = function(visible)
{
	visible = !!visible;
	if (visible === Sidebar.visible)
		return;
	Sidebar.visible = visible;
	$.cookies.set('sidebar-visible', Sidebar.visible);

    /*
	if (Sidebar.isDetachable)
	{
		// najpierw ukrywamy oba przyciski
		Sidebar._showButton.css('display', 'none');
		Sidebar._hideButton.css('display', 'none');
	}

	// ukrywamy lub chowamy sidebar
	Sidebar._sidebarContainer.css('display', visible?'block':'none');

	// zmieniamy klasę głównego kontenera i pokazujemy odpowiedni przycisk
	if (visible)
	{
		Sidebar._mainContentContainer.addClass('sidebar-visible');
		if (Sidebar.isDetachable)
			Sidebar._hideButton.css('display', 'block');
	}
	else
	{
		Sidebar._mainContentContainer.removeClass('sidebar-visible');
		if (Sidebar.isDetachable)
			Sidebar._showButton.css('display', 'block');
	}
*/
	Sidebar._notifyObservers();
};

/**
 * Usuwa sidebar.
 */
Sidebar.detach = function()
{
    Sidebar._mainContentContainer.
		removeClass('sidebar-visible sidebar-right sidebar-left');
	if (Sidebar.isDetachable)
	{
		Sidebar._hideButton.remove();
		Sidebar._showButton.remove();
	}
    Sidebar._sidebarContainer.remove();

	for (var property in this)
		delete this[property];
};

/**
 * Dodaje obserwatora. Obserwatorzy są powiadamiani po każdym pokazaniu lub
 * ukryciu sidebara. Każdy obserwator musi implementować metodę update(source),
 * gdzie parametr source to obserwowany obiekt.
 *
 * @param observer obserwator do dodania
 */
Sidebar.addObserver = function(observer)
{
	if (typeof observer.update != 'function')
		throw new Error('Obserwator nie posiada metody update(source)');
	Sidebar._observers.push(observer);
};

/**
 * Usuwa obserwatora. Wymaga się, żeby usuwany obserwator rzeczywiście był na
 * liście.
 *
 * @param observer obserwator do usunięcia
 */
Sidebar.removeObserver = function(observer)
{
	Sidebar._observers.removeElement(observer);
};

/**
 * Wysyła do obserwatorów powiadomienie.
 */
Sidebar._notifyObservers = function()
{
	var thisObj = this;
	Sidebar._observers.forEach(function(observer)
	{
		observer.update(thisObj);
	});
};
