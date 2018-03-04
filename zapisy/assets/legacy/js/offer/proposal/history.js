if (typeof Proposal == 'undefined') // todo scalić/wywalić
	Proposal = new Object();

Proposal.history = new Object();

Proposal.history.restoreButtonsAreReady = false;

Proposal.history.initRestoreButtons = function()
{
	if (Proposal.history.restoreButtonsAreReady)
		return;
	Proposal.history.restoreButtonsAreReady = true;

	$('.courserestore').click(function()
	{
		return !!confirm("Jesteś pewien?");
	});
};

Proposal.history.forcePOST = function()
{
    $('.without-js').hide();
    $('a.with-js').show();
    $('a.with-js').click(function()
    {
        $(this).parent().submit();
        return false;
    });
}

$(Proposal.history.forcePOST);

$(Proposal.history.initRestoreButtons);
