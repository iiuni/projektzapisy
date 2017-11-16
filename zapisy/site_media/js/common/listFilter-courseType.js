/**
 * Rozszerzenie klasy ListFilter o możliwość filtrowania po typach przedmiotów.
 *
 * @author Tomasz Wasilczyk (www.wasilczyk.pl)
 */

/**
 * Tworzy filtr typów przedmiotów. Filtr ma przypisaną nazwę "courseType"
 * i element ".course-type-filter".
 *
 * Po przypisaniu do formularza przekształca element (zawierający odpowiednie
 * kontrolki typów przedmiotów), grupując typy przedmiotów.
 *
 * @param matchCallback funkcja typu function(course, courseType)
 *        stwierdzająca, czy przedmiot "course" jest typu courseType
 */
ListFilter.CustomFilters.createCourseTypeFilter = function(matchCallback)
{
	var filter = new ListFilter.Filter('courseType', '.course-type-filter');
	filter.enabledTypes = new Object();
    filter.metaMode = true;
	filter.filterFormModel = null;

	var typeListIsEqual = function(typeList1, typeList2)
	{
		var type;
		for (type in typeList1)
			if (!typeList2[type])
				return false;
		for (type in typeList2)
			if (!typeList1[type])
				return false;
		return true;
	};

	filter.onAssign = function()
	{
		this.filterFormModel = new CourseTypeFilterForm(this.formElement.getDOM());
	};

	filter.serialize = function()
	{
		var enabledTypes = new Array();
		for (var type in this.enabledTypes)
			enabledTypes.push(type);
		return {
			metaMode: this.metaMode,
			enabledTypes: enabledTypes
		};
	};

	filter.deserialize = function(serialized)
	{
		/* jeżeli w zserializowanej wersji nie ma danych, to wczytujemy
		 * z formularza. TODO: przydało by się odczytywanie z formularza
		 * wszystkich typów (nie tylko zaznaczonych) i ustawienie ich
		 * (wszystkich) jako wybrane (czyli domyślnie wszystko pokazujemy)
		 */
		if (!serialized)
			return this.loadFromForm();

		var thisObj = this;

		var oldMetaMode = this.metaMode;
		this.metaMode = !!serialized.metaMode;
		
		var oldEnabledTypes = this.enabledTypes;
		this.enabledTypes = new Object();

		serialized.enabledTypes.forEach(function(type)
		{
			thisObj.enabledTypes[type] = true;
		});

		if (oldMetaMode != this.metaMode)
			return true;
		return !typeListIsEqual(oldEnabledTypes, this.enabledTypes);
	};

	filter.saveToForm = function()
	{
		this.filterFormModel.saveFilter(this);
	};

	filter.loadFromForm = function()
	{
		var oldMetaMode = this.metaMode;
		var oldEnabledTypes = this.enabledTypes;

		this.filterFormModel.readFilter(this);

		if (oldMetaMode != this.metaMode)
			return true;
		return !typeListIsEqual(oldEnabledTypes, this.enabledTypes);
	};

	filter.match = function(element)
	{
		for (var type in filter.enabledTypes)
			if (matchCallback(element, type))
				return true;
		return false;
	};

	return filter;
};


/*******************************************************************************
 * Model formularza filtrującego typy przedmiotów.
 ******************************************************************************/

/**
 * Konstruktor modelu formularza z filtrem po typach przedmiotów.
 *
 * @param container kontener, w którym jest formularz
 */
function CourseTypeFilterForm(container)
{
    if (!container)
        throw new Error('Kontener nie istnieje');
    var thisObj = this;
    var i;

    this.container = container;
    this.courseTypes = {};

    // generowanie nowej grupy - inne
//     var otherSpanBox = document.createElement('span');
//     otherSpanBox.className = 'checkbox';
//     var otherCheck = document.createElement('input');
//     otherCheck.type = 'checkbox';
// 	this.container.appendChild(otherSpanBox);
// 	otherSpanBox.appendChild(otherCheck);
//     otherCheck.value = '0';
//     otherCheck.id = 'filter-course-type-0';
//     otherCheck.className = 'filter-course-type-meta';
//     var otherGroup = document.createElement('input');
//     otherGroup.type = 'hidden';
//     otherGroup.className = 'group-id';
// 	otherSpanBox.appendChild(otherGroup);
//     var otherLabel = document.createElement('label');
//     otherSpanBox.appendChild(document.createTextNode(' '));
//     otherSpanBox.appendChild(otherLabel);
//     otherLabel.htmlFor = 'filter-course-type-0';
//     otherLabel.appendChild(document.createTextNode('Inne'));

    // akcja kliknięcia checkboxa meta-typu
    var metaClick = function(metaType)
    {
        $(metaType.checkbox).removeClass('partialCheck');
        var id = metaType.id;
        var check = metaType.checkbox.checked;
        for (i in thisObj.courseTypes)
        {
            var course = thisObj.courseTypes[i];
            if (course.isMeta)
                continue;
            if (course.getParent().id == id)
                course.checkbox.checked = check;
        }
    };

    // odczytywanie grup do obiektów
    var courseTypes = $(this.container).find('li.checkbox');
    for (i = 0; i < courseTypes.length; i++)
    {
        var type = new CourseTypeFilterForm.Type(courseTypes[i]);
        this.courseTypes[type.id] = type;
    }
    var otherType = this.courseTypes[0];
    if (!otherType)
        throw new Error('Nie wygenerowano grupy "Inne"');
    for (i in this.courseTypes)
    {
        var course = this.courseTypes[i];
        if (course.parent == null)
        {
            if (course.isMeta)
            {
                (function(sub) {
                    $(sub.checkbox).click(function()
                    {
                        metaClick(sub);
                    });
                })(course);
            }
            else
                course.parent = otherType;
        }
        else
        {
            if (course.isMeta)
                throw new Error('Nie obsługujemy modelu wielopoziomowego');
            if (!this.courseTypes[course.parent])
                throw new Error('Rodzic nie istnieje');
            course.parent = this.courseTypes[course.parent];
        }
    }

    this.metaSwitch = $("#extraCourseTypeFiltersToggle");
    $(this.metaSwitch).click(function()
    {
        thisObj.setMetaMode(!thisObj.metaMode);
    });

    this.setMetaMode(true);
}

/**
 * Ustawia, lub usuwa tryb meta-typów. Jeżeli jest włączony, to zamiast
 * normalnych typów przedmiotów w filtrze są wyświetlane ich grupy. Zaznaczanie
 * grupy skutkuje zaznaczeniem wszystkich jej elementów.
 *
 * @param enabled czy włączyć tryb meta-typów
 */
CourseTypeFilterForm.prototype.setMetaMode = function(enabled)
{
    var i;

    enabled = !!enabled;

    this.metaMode = enabled;
    $(this.metaSwitch).text(enabled ? 'pokaż więcej filtrów' : 'pokaż mniej filtrów');

    for (i in this.courseTypes)
    {
        var type = this.courseTypes[i];
        type.container.style.display = (this.metaMode == type.isMeta) ? '' : 'none';
    }

    if (this.metaMode)
    {
        // najpierw zaznaczamy wszystkie meta typy
        for (i in this.courseTypes)
        {
            var metaCourse = this.courseTypes[i];
            if (metaCourse.isMeta)
            {
                metaCourse.checkbox.checked = true;
                $(metaCourse.checkbox).removeClass('partialCheck');
            }
        }

        // teraz odznaczamy wszystkie, w których grupie choć jeden nie jest
        // zaznaczony
        var nonmetaCourse;
        for (i in this.courseTypes)
        {
            nonmetaCourse = this.courseTypes[i];
            if (nonmetaCourse.isMeta)
                continue;
            if (!nonmetaCourse.checkbox.checked)
                nonmetaCourse.getParent().checkbox.checked = false;
        }

        // a teraz "lekko" zaznaczamy te, w których grupie choć jeden jest
        // zaznaczony, a były odznaczone (czyli także jakiś jeden nie jest
        // zaznaczony)
        for (i in this.courseTypes)
        {
            nonmetaCourse = this.courseTypes[i];
            if (nonmetaCourse.isMeta)
                continue;
            if (nonmetaCourse.checkbox.checked)
            {
                var parentCheckbox = nonmetaCourse.getParent().checkbox;
                if (!parentCheckbox.checked)
                {
                    parentCheckbox.checked = true;
                    $(parentCheckbox).addClass('partialCheck');
                }
            }
        }
    }
};

/**
 * Odczytuje filtr z formularza.
 *
 * @param filter filtr (wygenerowany przez ListFilter.CustomFilters.
 *        createCourseTypeFilter()), który ma być ustawiony według danych
 *        z formularza
 */
CourseTypeFilterForm.prototype.readFilter = function(filter)
{
	filter.metaMode = this.metaMode;
    filter.enabledTypes = new Object();

    var courseTypes = $(this.container).find('input[type=checkbox]');
    for (var i = 0; i < courseTypes.length; i++)
    {
        if ($(courseTypes[i]).hasClass('filter-course-type-meta'))
            continue;

        var subKey = courseTypes[i].id;
        if (subKey.substr(0, 19) != 'filter-course-type-')
            throw new Error('Nieprawidłowy id pola');
        subKey = subKey.substr(19);
        if (courseTypes[i].checked)
			filter.enabledTypes[subKey] = true;
    }
};

/**
 * Ustawia formularz zgodnie z podanym filtrem.
 *
 * @param filter filter filtr (wygenerowany przez ListFilter.CustomFilters.
 *        createCourseTypeFilter()), według którego ma zostać ustawiony
 *        formularz
 */
CourseTypeFilterForm.prototype.saveFilter = function(filter)
{
    var courseTypes = $(this.container).find('input[type=checkbox]');
    for (var i = 0; i < courseTypes.length; i++)
    {
        var subKey = courseTypes[i].id;
        if (subKey.substr(0, 19) != 'filter-course-type-')
            throw new Error('CourseTypeFilter.readFilterFromForm: Nieprawidłowy id pola');
        subKey = subKey.substr(19);
        courseTypes[i].checked = !!filter.enabledTypes[subKey];
    }

    this.setMetaMode(filter.metaMode);
};

/**
 * Klasa pomocnicza pojedyńczego typu przedmiotu.
 *
 * @param container kontener, z którego jest inicjowany typ
 */
CourseTypeFilterForm.Type = function(container)
{
    var jqContainer = $(container);
    var jqCheckbox = jqContainer.children('input[type=checkbox]');

    this.container = container;
    this.isMeta = jqCheckbox.hasClass('filter-course-type-meta')
    this.checkbox = jqCheckbox[0];
    this.id = parseInt(this.checkbox.value);
	this.name = jqContainer.children('label').text().trim();

    var groupID = jqContainer.children('input.group-id')[0].value.trim();
    if (groupID == '')
        this.parent = null;
    else
    {
        groupID = parseInt(groupID);
        if (isNaN(groupID))
            throw new Error('CourseTypeFilterForm.Type: Zły ID grupy');
        this.parent = groupID;
    }
};

/**
 * Zwraca rodzica (meta-typ) typu przedmiotu. Jeżeli typ jest już rodzicem,
 * wyrzuca wyjątek.
 *
 * @return CourseTypeFilterForm.Type grupa, do której należy ten typ przedmiotów
 */
CourseTypeFilterForm.Type.prototype.getParent = function()
{
    if (this.isMeta)
        throw new Error('Węzeł jest rodzicem');
    if (this.parent == null)
        throw new Error('Pusty rodzic (powinien być inne)');
    if (typeof this.parent != 'object')
        throw new Error('Nie załadowano rodziców');
    return this.parent;
};
