if (typeof Poll == 'undefined')
    Poll = new Object();

Poll.results = Object()

Poll.results.init = function()
{
    var pid  = $('#poll-id').val();
    var mode = $('#display-mode').val();
    
    $('.connected-polls').hide();
    $('.result-groupped-list').hide();
	$('#results-by-course-list').hide();
    $('#courses-list-link').click( function(){
        $('#results-by-course-list').slideToggle(250);
        return false;
    });
    $('#results-by-teacher-list').hide();
    $('#teachers-list-link').click( function(){
        $('#results-by-teacher-list').slideToggle(250);
        return false;
    });
    $('.list-link').click(function(){
		$(this).parent().siblings('.result-groupped-list').slideToggle(250);
        return false;
	})

    $('#results-by-'+mode+'-'+pid).show();
    $('#results-by-'+mode+'-'+pid).parent().show();
    $('#results-by-'+mode+'-'+pid).parent().parent().show();
    
    if (pid != -1) {
        if (mode == 'course'){
            $('#results-by-course-list').show();
        }
        else if (mode == 'teacher'){
            $('#results-by-teacher-list').show();
        }
    }

    $('.show-other-ans-link').click(function(){
        $(this).parent().siblings('.hidden-answers').slideToggle(250);
        return false;
    })
    
    $('.section-link').click(function(){
        $(this).parent().siblings('table').slideToggle(250);
        return false;
    })
    
    $('.connected-link').click(function(){
        $(this).siblings('.connected-polls').slideToggle(250);
    })
}

$(Poll.results.init)

