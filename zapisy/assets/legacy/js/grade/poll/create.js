if (typeof Poll == 'undefined')
    Poll = new Object();


jQuery.validator.addMethod("have_sections", function(value, element) {
  return $('#sections-list-ul').children().size() > 0;
}, "Ankieta musi mieć pytania");

jQuery.validator.addClassRules("anysection", {
  have_sections: true
});

Poll.create = new Object();

Poll.create.init = function()
{

	Poll.create.submitted     = false;
    Poll.create.sections      = $('#sections');
    Poll.create.chosenSection = $('#sections-list').children('ul')[0];
    Poll.create.firstChosen   = $(Poll.create.sections).children()[0]

    $('.sectionid').each(function(i, elem){
        var value = $(elem).val();
        $(Poll.create.sections).children('option[value="'+ value +'"]').hide();
    })
    $('.poll-section-title').each(function(i, elem){
        var sectionRemove =  $('<img src="/static/images/remove-ico.png"'+
                           'class="remove" alt="usuń">');
        $(elem).after(sectionRemove);
        $(sectionRemove).click(function()
        {
            var li    = $(sectionRemove).closest('li');
            var value = $(li).find('.sectionid').val()
            $(li).remove();
            $(Poll.create.sections).children('option[value="'+ value +'"]').show();
        });
    });

    if( $("#group").children().size() < 2)
    {
        $('.type-visibility').hide();
        $('.group-visibility').hide();
        $(Poll.create.changeCourses)
    }

    $('#section-add').click(Poll.create.addSection);
    $('#semester').change(Poll.create.changeSemester);
    $('#courses').change(Poll.create.changeCourses);
    $('#type').change(Poll.create.changeTypes);


    $(Poll.create.chosenSection).sortable({handle : 'p'});
	$("form").keypress(function(e)
	{
  		if (e.which == 13)
  		{
    		return false;
  		}
	});
    $("#poll-create").validate();
}

$(Poll.create.init);

Poll.create.changeCourses = function()
{
    var course = $('#courses').val();
    
    if ( course > -1 )
    {
        $('.type-visibility').show();
        Poll.create.changeTypes();
    }
    else
    {
        $('.type-visibility').hide();
        $('.group-visibility').hide();
    }
}

Poll.create.changeTypes = function()
{
    var type    = parseInt($('#type').val());
    var course = parseInt($('#courses').val());
    if ( type > 0 && course > 0 )
    {
        $('.group-visibility').show();
        dataString = 'type=' + type + '&course=' + course
        $.ajax({
            type: "POST",
            url: "/grade/poll/ajax_get_groups",
            async: false,
            dataType: 'json',
            data: dataString,
            success: Poll.create.loadGroups
        });
    }
    if (type < 0)
    {
        $('.group-visibility').hide();
        
    }
}

Poll.create.loadGroups  = function(groups)
{
    $("#group").children().remove();
    $("#group").append( Poll.create.createOption('0', 'Wszystkie grupy') );
    $.each(groups, function(key, group)
    {
        $("#group").append( Poll.create.createOption( group[0], group[1] ) );
    });
}

Poll.create.changeSemester = function()
{
    var semester = $('#semester').val();
    dataString = 'semester=' + semester
    $.ajax({
        type: "POST",
        url: "/grade/poll/ajax_get_courses",
        async: false,
        dataType: 'json',
        data: dataString,
        success: Poll.create.loadCourses
    });
}

Poll.create.loadCourses = function(courses)
{
    $("#courses").children().remove();
    var item1 =  Poll.create.createOption('-1', 'Nie przypisane do przedmiotu')
    var item2 = Poll.create.createOption('0', 'Wszystkie grupy')
    $("#courses").append(item1);
    $("#courses").append(item2);
    $.each(courses, function(key, value)
    {
        $("#courses").append( Poll.create.createOption( value[0], value[1] ) );
    });

}

Poll.create.createOption = function(value, text)
{
    return $('<option></option>').val(value).html(text);
}

Poll.create.addSection = function()
{
    var value = $(Poll.create.sections).val();
    alert(value);
    if ( value === "-1" )
    {
        return false;
    }



    var newSection  = $('<li>');
    var sectionId   = $('<input type="hidden" class="sectionid" name="sections[]"' +
            ' value="'+ value +'">');

    $(newSection).append(sectionId);
    var section = Poll.create.getSection( value );
    $(newSection).append( $(section) )
	$(Poll.create.chosenSection).append(newSection)
      
    $( '#section-content-' + sectionId.value ).hide();
    $( '#section-toggle-' + sectionId.value ).text( '+' );
    $( '.grade-section-toggle-button' ).unbind( 'click' );
    $( '.grade-section-toggle-button' ).click( function(){
        var toToggleId  = $(this).attr( 'id' ).split( '-' )[2];
        var toToggleObj = $('#section-content-' + toToggleId );
        toToggleObj.slideToggle( 250 );
        if ( $(this).text() == '+' ){
            $(this).text( '-' );
        } else {
            if ( $(this).text() == '-' ) {
                $(this).text( '+' );
            }
        }
        return false;

    });
    var sectionRemove =  $('<img src="/static/images/remove-ico.png"'+
                           'class="remove" alt="usuń">');

    $('#poll-section-title-' + value).after(sectionRemove);
    $(sectionRemove).click(function()
    {
        $(newSection).remove();
        $(Poll.create.sections).children('option[value="'+ value +'"]').show();
    });
    $(Poll.create.sections).children('option[value="'+ value +'"]').hide();
    $(Poll.create.firstChosen).attr('selected', true);
}

Poll.create.getSection = function( section_id )
{
	var result;
	$.ajax({
        type: "POST",
        url: "/grade/poll/get_section/" + section_id + "/",
        async: false,
        success: function(data)
        {
			result = data;
        }
    });
    return result
}

