/*
 * 'Fajny' dialog box.
 * Using:
 *  1. add:
 *         {% include 'common/dialog_box.html' %} any place in template
 *  2. add:
 *        <link rel="stylesheet" href="/static/css/common/dialog_box.css" type="text/css" />
 *  3. add:
 *      <script src="/static/js/common/dialog_box.js" type="text/javascript"></script>
 *  4. Fereol.dialog.setHTML( html ) - adding html to dialog box
 *  5. Fereol.dialog.show()          -
 */

if (typeof Fereol == 'undefined')
    Fereol = new Object();

Fereol.dialog = new Object();

Fereol.dialog.init = function()
{
    $('#box-exit').click( Fereol.dialog.hide )
}

Fereol.dialog.show = function()
{
    $('body').css('overflow', 'hidden');
    $('#screen').css({  "display": "block"});
    $('#box').css({"display": "block"});
    $('#backscreen').css('display', 'block');
    $('#box-exit').click( Fereol.dialog.hide );
    $('#box').focus();
}

$(Fereol.dialog.init);

Fereol.dialog.setTitle = function(html)
{
    $('#box-title').html(html);
}

Fereol.dialog.addButton = function( button )
{
    $('#box-button').html( button + $('#box-button').html() )
    $('#box-exit').click( Fereol.dialog.hide )
}

Fereol.dialog.setHTML = function(html)
{
    $('#box-content').html( html );
}

Fereol.dialog.hide = function()
{
    $('body').css('overflow', 'auto');
    $('#screen').css({  "display": "none"});
    $('#box').css({"display": "none"});
    $('#backscreen').css('display', 'none');
}
