Correction = new Object()


Correction.init = function()
{
    $('li.od-vote-course select').each(function(elem)
    {
        //$(this).remove();
        var vote = $(this).parent().find('.value').val()

        $(this).find('option').each(function(){
           if( $(this).attr('value') <vote )
           {
               $(this).remove();
               
           }
        });
    })
}

$(Correction.init);