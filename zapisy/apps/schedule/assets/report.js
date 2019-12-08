import "jquery";
const $ = jQuery;


$(document).ready(() => {
	$('#select_all_button').click((event) => {
		$('#id_rooms option').prop('selected', true);    
	    console.log("Hello");
	});

});
