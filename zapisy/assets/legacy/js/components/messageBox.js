/**
 * Klasa komunikatów do wyświetlania w formularzach.
 */

function MessageBox(message)
{
    this.message = $.trim(message);

    this.box = document.createElement('div');
    this.box.className = 'main-message';
    $(this.box).text(this.message);
}

/**
 * Wyświetla komunikat o podanej treści na początku strony właściwej.
 *
 * @param message komunikat do wyświetlenia
 */
MessageBox.display = function(message)
{
    var messageBox = new MessageBox(message)
    $('#main-content').prepend(messageBox.box);
    $(window).scrollTop($(messageBox.box).offset()['top']);
};

/**
 * Usuwa wszystkie komunikaty (również te nie wygenerowane przez javascript).
 */
MessageBox.clear = function()
{
    $('.main-message').remove();
};
