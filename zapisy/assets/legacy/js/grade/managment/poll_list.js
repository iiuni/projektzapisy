if (typeof Poll == 'undefined')
    Poll = new Object();

Poll.list = new Object();


Poll.list.init = function()
{
    $('#go_to_page').change(function()
    {
        $('#filter-form').attr('action', '?' + $(this).val() ).submit();
    })

    $('.link').click(function(e)
    {
        $('#filter-form').attr('action', $(this).attr('href')).submit();
        e.preventDefault()
    })

    $('.poll_list_a').click(function()
    {
        var html = Poll.list.getHTML( $(this).attr('href') )
        Fereol.dialog.setHTML(html);
        Fereol.dialog.setTitle("Podgląd ankiety");
        Fereol.dialog.show();
        $('#box-belt-edit').remove();
        if(! $(this).parent().parent().find('._selected_action').attr('disabled') )
        {
            var button = "<input type='button' value='Edytuj' id='box-belt-edit'>"
            Fereol.dialog.addButton(button);
        }
        $('#box-belt-edit').click(function()
        {
            var html = Poll.list.getHTML( $("#edit_url").val() );
            Fereol.dialog.setHTML(html);
            Fereol.dialog.setTitle("Edycja ankiety");
            Poll.create.init();
            $(this).hide();
            return false;
        });
        return false;
    })
    $('.section_list_a').click(function()
    {
        var html = Poll.list.getHTML( $(this).attr('href') )
        Fereol.dialog.setHTML(html);
        Fereol.dialog.setTitle("Podgląd sekcji")
        Fereol.dialog.show();
        $('#box-belt-edit').remove();
        if(! $(this).parent().parent().find('._selected_action').attr('disabled') )
        {
            var button = "<input type='button' value='Edytuj' id='box-belt-edit'>"
            Fereol.dialog.addButton(button);
        }
        Poll.section.showEdit();

        $('#box-belt-edit').click(function()
        {
            Fereol.dialog.setTitle("Edycja sekcji")
            $('.section-edit').show();
            $('.section-show').remove();
            $('.only-edit').show();
            $('.only-show').hide();
            Poll.section.editParser();
            $(this).hide();
            return false;
        });
        return false;
    })

    $('#new-section').click(function(event)
    {
        event.preventDefault();
        $('#new-section').click(function(event){event.preventDefault();$('.modal').show();})
    })

    $('#new-poll').click(function()
    {
        var html = Poll.list.getCreatePoll();
        Fereol.dialog.setHTML( html )
        Fereol.dialog.setTitle("Nowa ankieta")
        Fereol.dialog.show();
        Poll.create.init();
        return false;
    })

    $('#new-template').click(function()
    {
        var html = Poll.list.getCreateTemplate();
        Fereol.dialog.setHTML( html )
        Fereol.dialog.setTitle( "Nowy szablon")
        Fereol.dialog.show();
        Poll.create.init();
        return false;
    })

    $('.show_template').click(function()
    {
        var html = Poll.list.getHTML( $(this).attr('href') )
        Fereol.dialog.setHTML(html);
        Fereol.dialog.setTitle("Podgląd szablonu")
        Fereol.dialog.show();
        return false;
    });
}

$(Poll.list.init);

Poll.list.getCreateTemplate = function( )
{
    return Poll.list.getHTML('/grade/poll/managment/templates/form/');
}

Poll.list.getCreateSection = function( )
{
    return Poll.list.getHTML('/grade/poll/managment/section/form/');
}

Poll.list.getCreatePoll = function( )
{
    return Poll.list.getHTML('/grade/poll/managment/poll/form/');
}

Poll.list.getHTML = function( link )
{
	var result;
	$.ajax({
        type: "POST",
        url: link,
        async: false,
        success: function(data)
        {
			result = data;
        }
    });
    return result
}

