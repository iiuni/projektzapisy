if (typeof Poll == 'undefined')
    Poll = new Object();

Poll.answer = Object()

Poll.answer.init = function()
{
	$('.grade-fillable-poll-sublist').hide();
	var pid = $('#poll-form-id').val();
	$('.grade-fillable-poll-link').click(function()
	{
		$(this).siblings('ul').slideToggle(250);
		return false;
	})
	$('#grade-fillable-poll-link-'+pid).parent().parent().show();
	$('.poll-section-radio-hideon:checked').each(function()
    {
    	$(this).parents('.poll-section-leading').nextAll().hide()
    })
    $('.poll-section-radio-hideon').change(function()
    {
    	$(this).parents('.poll-section-leading').nextAll().hide()
    })
    
    $('.poll-section-radio-all').change(function()
    {
    	var father = $(this).parents('.poll-section-leading');
        $(father).nextAll().show()
    });
    $('.poll-section-leading').nextAll().hide();
    
    $('input[value="-1"].poll-section-choice:not(:checked)').each(Poll.answer.hideOther);
    $('#poll-form').submit(Poll.answer.cleanup);
    $('.poll-section-choicelimit-choice').change(Poll.answer.choices_limit)
    $('input[value="-1"].poll-section-choice').change(Poll.answer.other)
    var finished = parseInt($('#finished-polls').text())
    var all      = parseInt($('#all-polls').text())
    var percent  = parseInt(finished/all * 100)
    $("#progressbar").progressbar({ value: percent });
	$("form").keypress(function(e)
	{
  		if (e.which == 13)
  		{
    		return false;
  		}
	});
}

Poll.answer.hideOther = function()
{
	$(this).siblings('.poll-section-other').hide();
}

Poll.answer.other = function()
{
	if($(this).attr('checked'))
	{
		$(this).siblings('.poll-section-other').show();
	}
	else
	{
		$(this).siblings('.poll-section-other').hide();
		
	}
}

Poll.answer.cleanup = function()
{
	$('.poll-section-radio-hideon:checked').each(function()
    {
    	$(this).parents('.poll-section-leading').nextAll().each(function()
    	{
    		$(this).find('input:checked').attr('checked', false);
			$(this).find('input[type=text]').val('');
    	})
    })
}

Poll.answer.choices_limit = function()
{
	if( $(this).attr('checked') )
	{
		var parent  = $(this).parent().parent()
		var limit   = $(parent).siblings('.poll-section-answer-limit').val()
		var checked = $(parent).find('.poll-section-choicelimit-choice:checked').length
		
		if (limit == null || limit == 0)
		{
			limit = checked
		}
		if (limit < checked)
		{
			$(this).attr('checked', false);
			if( $(this).hasClass('poll-section-choice') )
			{
				$(this).siblings('.poll-section-other').hide();
			}
		}
	}
}

$(Poll.answer.init)

