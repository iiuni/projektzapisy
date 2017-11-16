/**
 * Model uniwersalnego filtra listy dowolnych obiektów, opartego o formularz
 * html.
 *
 * @author Tomasz Wasilczyk (www.wasilczyk.pl)
 */

/**
 * Konstruktor filtra listy obiektów.
 *
 * @param name nazwa filtra (używana m.in. do nazywania cookie)
 * @param formContainer kontener z formularzem filtrowania
 */
function ListFilter(name, formContainer)
{
	var thisObj = this;
	
	this.filters = new Array();
	this.objectsList = new Array();
	this.name = name;
	this.formContainer = $(formContainer);

	// filtr główny, "zawierający" wszystkie inne

	this.mainFilter = new ListFilter.Filter(name);

	this.mainFilter.serialize = function()
	{
		var serialized = new Object();
		thisObj.filters.forEach(function(filter)
		{
			serialized[filter.name] = filter.serialize();
		});
		return serialized;
	};

	this.mainFilter.deserialize = function(serialized)
	{
		var stateChanged = false;
		thisObj.filters.forEach(function(filter)
		{
			if (filter.deserialize(serialized[filter.name]))
				stateChanged = true;
		});
		return stateChanged;
	};

	this.mainFilter.saveToForm = function()
	{
		thisObj.filters.forEach(function(filter)
		{
			filter.saveToForm();
		});
	};

	this.mainFilter.loadFromForm = function()
	{
		var stateChanged = false;
		thisObj.filters.forEach(function(filter)
		{
			if (filter.loadFromForm())
				stateChanged = true;
		});
		return stateChanged;
	};

	this.mainFilter.match = function(element)
	{
		var matchOK = true;

		thisObj.filters.forEach(function(filter)
		{
			if (!matchOK)
				return;
			if (!filter.match(element))
				matchOK = false;
		});

		return matchOK;
	}

	// filtr główny - koniec
}

/**
 * Wykonuje filtrowanie.
 */
ListFilter.prototype.doFilter = function()
{
	var thisObj = this;
	var matchedElementsCount = 0;
	var matchedElements = [];
	this.objectsList.forEach(function(element)
	{
		var matches = thisObj.mainFilter.match(element);
		element.setVisible(matches);
		if (matches)
		{
			matchedElementsCount++;
			matchedElements.push(element);
		}
	});
	this.afterFilter(matchedElementsCount, matchedElements);
};

/**
 * Wykonywany po filtrowaniu (które przyniosło zmiany) - do przeciążenia.
 *
 * @todo parametr matchedElementsCount do usunięcia, na razie zachowujemy ze wzgl. na zgodność API
 * @param matchedElementsCount liczba elementów pasujących do filtra
 * @param matchedElements elementy pasujące do filtra
 */
ListFilter.prototype.afterFilter = function(matchedElementsCount, matchedElements) {}

/**
 * Uruchamia wątek filtrowania.
 *
 * @param doNotLoadCookie true, jeżeli ma nie wczytywać cookie
 */
ListFilter.prototype.runThread = function(doNotLoadCookie)
{
	var thisObj = this;

	if (this.threadIsRunning)
		return;
	this.threadIsRunning = true;

	if (!doNotLoadCookie)
	{
		var serialized = $.cookies.get('listFilter-' + this.name);

		if (serialized)
		{
			// niezależnie, czy coś się wczyta, firstRun spowoduje użycie filtra
			this.mainFilter.deserialize(serialized);
			this.mainFilter.saveToForm();
		}
	}

	var firstRun = true;
	var filterThread = function()
	{
		if (!thisObj.threadIsRunning)
			return;
		if (thisObj.mainFilter.loadFromForm() || firstRun)
		{
			$.cookies.set('listFilter-' + thisObj.name, thisObj.mainFilter.serialize());
			thisObj.doFilter();
		}

		firstRun = false;

		setTimeout(filterThread, 50);
	};

	filterThread();
};

/**
 * Dodaje nowy obiekt do filtrowanej listy.
 *
 * @param element nowy obiekt
 */
ListFilter.prototype.addElement = function(element)
{
	this.objectsList.push(element);
	element.setVisible(this.mainFilter.match(element));
};

/**
 * Czyści listę filtrowanych elementów.
 */
ListFilter.prototype.clearElements = function()
{
	this.objectsList = new Array();
}

/**
 * Dodaje do zbioru filtrów nowy.
 *
 * @param filter nowy filtr (instancja ListFilter.Filter)
 */
ListFilter.prototype.addFilter = function(filter)
{
	if (!filter)
	{
		var error = new Error('Nie podano filtra');
		$.logException(error);
		throw error;
	}
	filter.assignFormContainer(this.formContainer);
	this.filters.push(filter);
};


/*******************************************************************************
 * Gotowe filtry proste.
 ******************************************************************************/

ListFilter.CustomFilters = new Object();

/**
 * Tworzy prosty filtr tekstowy.
 *
 * @param name nazwa filtra
 * @param formElementSelector nazwa klasy elementu formularza, przechowującego tekst
 * @param matchCallback funkcja typu function(element, value) stwierdzająca, czy
 *        element "element" pasuje do filtra w stanie "value"
 */
ListFilter.CustomFilters.createSimpleTextFilter = function(name, formElementSelector, matchCallback)
{
	var filter = new ListFilter.Filter(name, formElementSelector + '[type=text]');
	filter.value = '';

	filter.serialize = function()
	{
		return filter.value;
	};

	filter.deserialize = function(serialized)
	{

        var val = $(formElementSelector).val();

        if (filter.value == serialized &&  val === '' )
      			return false;

        if ( val !== '' ){
            filter.value = val;
        } else {
		    filter.value = serialized;
        }
		return true;
	};

	filter.saveToForm = function()
	{
		this.formElement.attr('value', this.value);
	};

	filter.loadFromForm = function()
	{
		var newValue = this.formElement.attr('value');
		if (this.value == newValue)
			return false;

		this.value = newValue;
		return true;
	};

	filter.match = function(element)
	{
		return matchCallback(element, filter.value);
	};

	return filter;
};

/**
 * Tworzy prosty filtr logiczny (włącz / wyłącz).
 *
 * @param name nazwa filtra
 * @param formElementSelector nazwa klasy elementu formularza, przechowującego stan (checkbox)
 * @param matchCallback funkcja typu function(element, value) stwierdzająca, czy
 *        element "element" pasuje do filtra w stanie "value"
 */
ListFilter.CustomFilters.createSimpleBooleanFilter = function(name, formElementSelector, matchCallback)
{
	var filter = new ListFilter.Filter(name, formElementSelector + '[type=checkbox]');
	filter.value = false;

	filter.serialize = function()
	{
		return filter.value?'1':'0';
	};

	filter.deserialize = function(serialized)
	{
		if (serialized == 0)
			serialized = 0;
		serialized = !!serialized;

		if (filter.value == serialized)
			return false;

		filter.value = serialized;
		return true;
	};

	filter.saveToForm = function()
	{
		this.formElement.attr('checked', this.value);
	};

	filter.loadFromForm = function()
	{
		var newValue = this.formElement.attr('checked');
		if (this.value == newValue)
			return false;

		this.value = newValue;
		return true;
	};

	filter.match = function(element)
	{
		return matchCallback(element, filter.value);
	};

	return filter;
};

/**
 * Tworzy prosty filtr wyboru z listy.
 *
 * @param name nazwa filtra
 * @param formElementSelector nazwa klasy elementu formularza, przechowującego wybór (select)
 * @param matchCallback funkcja typu function(element, option) stwierdzająca, czy
 *        element "element" pasuje do filtra w stanie "option"
 */
ListFilter.CustomFilters.createSimpleComboFilter = function(name, formElementSelector, matchCallback)
{
	var filter = new ListFilter.Filter(name, 'select' + formElementSelector);
	filter.value = null;
	filter.controlValue = null; // wartość ustawiona na kontrolce
	filter.valueList = new Array();

	filter.onAssign = function()
	{
		var thisObj = this;
		this.valueList = new Array();
		this.formElement.children('option').each(function(i, option)
		{
			option = $(option);
			thisObj.valueList.push(option.attr('value'));
		});

		var onChange = function()
		{
			thisObj.controlValue = thisObj.formElement.val();
		};
		this.formElement.change(onChange);
		onChange();
	};

	filter.serialize = function()
	{
		return filter.value;
	};

	/**
	 * Sprawdza, czy wartość jest poprawna.
	 *
	 * @param rawValue sprawdzana wartość
	 * @return rawValue, jeżeli wartość jest poprawna; null w p. p.
	 */
	filter.validateValue = function(rawValue)
	{
	//	if (filter.valueList.indexOf(rawValue + '') >= 0)
			return rawValue;
		return null;
	};

	filter.deserialize = function(serialized)
	{
		if (filter.value == serialized)
			return false;

		filter.value = this.validateValue(serialized);
		return true;
	};

	filter.saveToForm = function()
	{
		this.controlValue = this.value;
		this.formElement.val(this.value);
	};

	filter.loadFromForm = function()
	{
		var newValue = this.controlValue;//this.formElement.attr('value');
		if (this.value == newValue)
			return false;
        
// 		if (this.validateValue(newValue) === null)
// 			throw new Error('Wartość odczytana z formularza nie przechodzi walidacji');

		this.value = newValue;
		return true;
	};

	filter.match = function(element)
	{
		return matchCallback(element, filter.value);
	};

	return filter;
};


/*******************************************************************************
 * Obiekt (do "dziedziczenia") elementu listy.
 ******************************************************************************/

ListFilter.Element = function(data, setVisibleMethod)
{
	this.data = data;
	if (setVisibleMethod)
		this.setVisible = setVisibleMethod;
}

/**
 * Ustawia widoczność obiektu. Metoda wykonywana po stwierdzeniu, czy obiekt
 * pasuje do podanego filtra.
 *
 * @param visible true, jeżeli obiekt pasuje do filtra
 */
ListFilter.Element.prototype.setVisible = function(visible)
{
	throw newError('Nie przeciążono');
}


/*******************************************************************************
 * Obiekt (do "dziedziczenia") mini-filtra, które się składają na filtr główny.
 ******************************************************************************/

ListFilter.Filter = function(name, formElementSelector)
{
	this.name = name;
	this.formElement = null;
	if (!formElementSelector)
		formElementSelector = null;
	this.formElementSelector = formElementSelector;
};

/**
 * Przypisuje do filtra kontener formularza, w ramach którego ma szukać swoich
 * kontrolek (z których pobiera swój stan) i przypisuje znalezioną kontrolkę.
 */
ListFilter.Filter.prototype.assignFormContainer = function(formContainer)
{
	if (this.formElementSelector)
		this.formElement = formContainer.find(this.formElementSelector).assertOne();
	this.onAssign();
};

/**
 * Zdarzenie wywoływane po przypisaniu do (elementu) formularza.
 */
ListFilter.Filter.prototype.onAssign = function() { };

/**
 * Zapisuje stan filtra jako string.
 */
ListFilter.Filter.prototype.serialize = function()
{
	throw newError('Nie przeciążono');
};

/**
 * Wczytuje stan filtra ze stringa.
 *
 * @param serializedFilter zserializowany stan filtra
 * @return true, jeżeli stan się zmienił
 */
ListFilter.Filter.prototype.deserialize = function(serializedFilter)
{
	throw newError('Nie przeciążono');
};

/**
 * Zapisuje stan filtra do formularza html.
 */
ListFilter.Filter.prototype.saveToForm = function()
{
	throw newError('Nie przeciążono');
};

/**
 * Odczytuje stan filtra z formularza html.
 *
 * @return true, jeżeli stan się zmienił
 */
ListFilter.Filter.prototype.loadFromForm = function()
{
	throw newError('Nie przeciążono');
};

/**
 * Sprawdza, czy element pasuje do filtra (przy określonym stanie).
 *
 * @param element element listy (instancja ListFilter.Element)
 * @return true, jeżeli pasuje
 */
ListFilter.Filter.prototype.match = function(element)
{
	throw newError('Nie przeciążono');
};
