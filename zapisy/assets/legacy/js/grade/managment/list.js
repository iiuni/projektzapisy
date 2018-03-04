if (typeof List == 'undefined')
    List = new Object();
    
List.checkbox = new Object();

List.checkbox.init = function()
{
	List.checkbox.calc()
	$('#action-toggle').change(List.checkbox.changeAll)
	$('._selected_action').change(List.checkbox.change)
}

$(List.checkbox.init)

List.checkbox.changeAll = function()
{
	if( $(this).attr('checked') )
	{
		$('._selected_action').attr('checked', true)
        $('._selected_action:disabled').attr('checked', false)
	}
	else
	{
		$('._selected_action').attr('checked', false)		
	}
	List.checkbox.calc()
}

List.checkbox.change = function()
{
	if( $(this).attr('checked') )
	{
		List.checkbox.checked = List.checkbox.checked + 1
	}
	else
	{
		List.checkbox.checked = List.checkbox.checked - 1
	}
	$('#object_count').text(List.checkbox.checked);
}

List.checkbox.calc = function()
{
	List.checkbox.checked = 0;
	$('._selected_action').each(function()
	{
		if( $(this).attr('checked') ) List.checkbox.checked = List.checkbox.checked + 1;
	});
	$('#object_count').text(List.checkbox.checked);
}
