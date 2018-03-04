if (typeof Proposal == 'undefined') // todo scalić/wywalić
	Proposal = new Object();

Proposal.form = new Object();

Proposal.form.init = function()
{
	Proposal.form.bookList = $('#od-proposal-form-books').children('ul')[0];

	$(Proposal.form.bookList).sortable({handle : 'img.move'});

	$('#od-proposal-form-name').focus();
};

$(Proposal.form.init);

