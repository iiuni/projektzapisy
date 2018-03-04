if (typeof Proposal == 'undefined') // todo scalić/wywalić
	Proposal = new Object();

Proposal.view = new Object();

Proposal.view.deleteButtonsAreReady = false;

Proposal.view.initDeleteButtons = function()
{
	if (Proposal.view.deleteButtonsAreReady)
		return;
	Proposal.view.deleteButtonsAreReady = true;

	$('.proposal-delete').click(function()
	{
		return !!confirm("Jesteś pewien?");
	});
};

Proposal.view.forcePOST = function()
{
    $('.without-js').hide();
    $('a.with-js').show();
    $('a.with-js').click(function()
    {
        $(this).parent().submit();
        return false;
    });
}

$(Proposal.view.forcePOST);
$(Proposal.view.initDeleteButtons);
