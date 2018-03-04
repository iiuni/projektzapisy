if (typeof Ticket == 'undefined')
    Ticket = new Object();
    
Ticket.keys_generate = new Object()

Ticket.keys_generate.init = function()
{

    if( $('#keys_to_create').text().castToInt() > 0)
    {
        var html = "<div><span>Trwa generowanie kluczy</span>( <span id='keys-percent'>0</span> % )<div id='progressbar'></div></div>"
        $('#creator').html(html);
    	$("#progressbar").progressbar({ value: 0 });
	    Ticket.keys_generate.keys   = $('#keys_to_create').text().castToInt()
        Ticket.keys_generate.start();
    }
}

Ticket.keys_generate.start = function()
{
	$.ajax({
        type: "POST",
        url: url_generate,
        success: Ticket.keys_generate.finish
    });
    Ticket.keys_generate.interval = setInterval( "Ticket.keys_generate.progress()", 2000 );
}

Ticket.keys_generate.progress = function()
{
	$.ajax({
        type: "POST",
        url: url_progress,
        success: Ticket.keys_generate.update
    });
}

Ticket.keys_generate.finish = function(result)
{
	clearInterval(Ticket.keys_generate.interval)
	$( "#progressbar" ).progressbar( "option", "value", 100 );
	$( "#keys-percent" ).text('100');
}

Ticket.keys_generate.update = function(result)
{
	var done    = parseInt(result);
	var all     = Ticket.keys_generate.keys
	var percent = parseInt ((done/all) * 100)
	$( "#keys-percent" ).text(percent);
	$( "#progressbar" ).progressbar( "option", "value", percent );
	
}

$(Ticket.keys_generate.init);

