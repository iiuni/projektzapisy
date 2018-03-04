/**
 * Rozszerzenia do podstawowej funkcjonalności jQuery.
 *
 * @author Tomasz Wasilczyk (www.wasilczyk.pl)
 */

if (!String.prototype.trim) // IE8 <3
	String.prototype.trim = function(charList)
	{
		if (charList)
			charList = '[' + charList + ']';
		else
			charList = '\\s';
		return this.replace(new RegExp('^' + charList + '+|' + charList + '+$', 'g'), '');
	};

String.prototype.castToInt = function(acceptNull)
{
	if (acceptNull && !this.trim()){
		return null;}
	var val = parseInt(this.trim());
	if (isNaN(val))
		throw new Error('Nieprawidłowa wartość');
	return val;
};

Number.prototype.castToInt = function()
{
	if (this % 1 != 0)
		throw new Error('Nieprawidłowa wartość (liczba zmiennoprzecinkowa)');
	return parseInt(this);
};

String.prototype.castToBool = function()
{
	var val = this.trim();
	if (val.toLowerCase() == 'true')
		return true;
	if (val.toLowerCase() == 'false')
		return false;
	throw new Error('Nieprawidłowa wartość');
};

String.prototype.removePrefix = function(prefix)
{
	if (this.indexOf(prefix) != 0)
		throw new Error('Prefiks nie pasuje do ciągu');
	return this.substr(prefix.length);
};

String.prototype.lpad = function(padStr, length)
{
	var add = length - this.length;

	if (add <= 0)
		return String(this);

	padStr = (new Array(Math.ceil(add / padStr.length) + 1)).join(padStr).
		substr(0, add);

    return (padStr + this);
};

String.prototype.capitalize = function()
{
	return this.charAt(0).toUpperCase() + this.slice(1);
};

if (!Array.prototype.indexOf)
	Array.prototype.indexOf = function(value)
	{
		for (var i = 0; i < this.length; i++)
			if (this[i] == value)
				return i;
		return -1;
	};

if (!Array.prototype.forEach) // IE8 <3
	Array.prototype.forEach = function(callback)
	{
		for (var i = 0; i < this.length; i++)
			callback(this[i], i, this);
	};

Array.prototype.remove = function(index, count)
{
	if (typeof count == 'undefined')
		count = 1;
	if (index < 0)
		index += this.length;
	if (count <= 0)
		throw new Error('not positive count');
	if (index < 0 || index >= this.length || index + count > this.length)
		throw new Error('index out of bounds');

	var tail = this.slice(index + count);
	this.length = index;
	return this.push.apply(this, tail);
};

Array.prototype.removeElement = function(element)
{
	var index = this.indexOf(element);
	if (index < 0)
		throw new Error('Element not found');
	return this.remove(index, 1);
};

jQuery.log = function(message)
{
	if(window.console)
		console.debug(message);
//	else
//		alert(message);
};

jQuery.logException = function(exception)
{
	if(window.console)
	{
		console.log(exception.stack);
		console.exception(exception);
	}
};

jQuery.event.props.remove(jQuery.event.props.indexOf('charCode'));

jQuery.fn.assertOne = function()
{
	var error;
	
	if (this.length == 0)
	{
		error = new Error('Element nie istnieje');
		$.logException(error);
		throw error;
	}
	if (this.length > 1)
	{
		error = new Error('Więcej niż jeden element');
		$.logException(error);
		throw error;
	}
	return this;
};

jQuery.fn.getDOM = function()
{
	return this.assertOne().get(0);
};

jQuery.create = function(type, parameters)
{
	var obj = document.createElement(type);
	for (param in parameters)
		obj[param] = parameters[param];
	return $(obj);
};

jQuery.createText = function(contents)
{
	return $(document.createTextNode(contents));
};

jQuery.fn.disableDragging = function()
{
	this.bind('mousedown mousemove selectstart', function(e)
	{
		if (e && e.preventDefault)
			e.preventDefault();
		return false;
	});

	this.css('MozUserSelect', 'none');
	
	return this;
};

jQuery.fn.changeTagType = function(target, copyAttributes)
{
	var collection = this;

	this.each(function(index, element)
	{
		element = $(element);
		var attributes = {};

		if (copyAttributes)
			for (i = 0; i < copyAttributes.length; i++)
			{
				var k = copyAttributes[i];
				var v = element.attr(k);
				if (v)
					attributes[k] = v;
			}

		var replacement = jQuery.create(target).insertBefore(element);
		var contents = element.contents();
		contents.detach();
		replacement.append(contents);
		element.remove();
		replacement.attr(attributes);

		collection[index] = replacement.getDOM();
	});

	return this;
};

jQuery.fn.scrollTo = function(options)
{
	var scrollDestination = this.assertOne().offset().top;
	$('html, body').animate(
	{
		scrollTop: scrollDestination + 'px'
	}, options);

	return this;
};

jQuery.fn.maximizeWidth = function()
{
	var border = this.outerWidth() - this.innerWidth();
	this.width(this.parent().width() - this.position().left - border);
	return this;
};

jQuery.fn.appendSpace = function()
{
	return this.append($.createText(' '));
};

AjaxMessage = function()
{
	this.type = null;
	this.code = null;
	this.message = null;
	this.data = null;
};

AjaxMessage.fromJSON = function(raw)
{
	var message = new AjaxMessage();
	message.type = raw.type.trim();
	message.code = raw.code.trim();
	message.message = raw.message.trim();
	message.data = raw.data;

	return message;
};

AjaxMessage.prototype.isSuccess = function()
{
	return (this.type == 'success');
};

AjaxMessage.prototype.isFailure = function()
{
	return (this.type == 'failure');
};

AjaxMessage.prototype.displayMessageBox = function()
{
	MessageBox.display(this.message);
};

AjaxMessage.prototype.toString = function()
{
	if (this.isSuccess())
		return 'AjaxSuccessMessage';
	else if (this.isFailure())
		return 'AjaxFailureMessage';
	else
		return 'AjaxMessage';
};

/**
 * Zarządzanie automatycznym odświeżaniem danych.
 */

jQuery.dataInvalidate_check = function()
{
	jQuery.dataInvalidate_input = $('input[name=data-invalidated]').assertOne();
	jQuery.dataInvalidate_invalidated =
		(jQuery.dataInvalidate_input.attr('value') == 'yes');
	jQuery.dataInvalidate_input.attr('value', 'no');
	if (jQuery.dataInvalidate_invalidated)
	{
		jQuery.dataInvalidate_invalidated = false;
		document.location = document.location;
	}
};

jQuery.dataInvalidate = function()
{
	if (jQuery.dataInvalidate_invalidated)
		return;
	jQuery.dataInvalidate_invalidated = true;
	jQuery.dataInvalidate_input.attr('value', 'yes');
};
