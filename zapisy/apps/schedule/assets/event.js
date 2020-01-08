import "jquery";
const $ = jQuery;

const STATUS_ACCEPTED = '1';
const STATUS_REJECTED = '2';

function sumbitDecisionForm() {
	$("#decision_form").submit();
}

// dostosuj przyciski dotyczące zaakceptowania lub odrzucenia wydarzenia
function adjustButtonsDecision() {
	var $currentState = $('#decision').val(); 
	switch($currentState) {
		case STATUS_ACCEPTED:
			$('#accept_button').prop('disabled', true);
			break;
		case STATUS_REJECTED:
			$('#reject_button').prop('disabled', true);
			break;
	}
}

$(document).ready(() => {

	adjustButtonsDecision();

	// zmień wartość ukrytego pola informującego o rodzaju decyzji na akceptację
	$('#accept_button').click(function() {
	    $('#decision').val(STATUS_ACCEPTED);
	    sumbitDecisionForm();
	});

	// zmień wartość ukrytego pola informującego o rodzaju decyzji na odrzucenie
	$('#reject_button').click(function() {
	    $('#decision').val(STATUS_REJECTED);
	    sumbitDecisionForm(); 
	});
});