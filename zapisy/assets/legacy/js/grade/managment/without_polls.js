/**
 * Created by .
 * User: iks
 * Date: 5/24/11
 * Time: 7:17 PM
 */


if (typeof Poll == 'undefined')
    Poll = new Object();



Poll.without = new Object();

Poll.without.init = function()
{
    $('#poll-managment-list > li > a').click(Poll.without.create);
}

$(Poll.without.init);

Poll.without.create = function(e)
{
    var html = Poll.without.getHTML(  $(this).attr('href')  );
    Fereol.dialog.setHTML( html )
    Fereol.dialog.setTitle("Nowa ankieta")
    Fereol.dialog.show();
    Poll.create.init();

    e.preventDefault()

}

Poll.without.getHTML = function( link )
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
