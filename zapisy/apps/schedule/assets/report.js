import "jquery";
import "print-this";
const $ = jQuery;


$(document).ready(() => {
	$('#select_all_button').click((event) => {
		$('#id_rooms option').prop('selected', true);    
	});

	$('#reportForm').submit(function() { // catch the form's submit event
        $.ajax({ // create an AJAX call...
            data: $(this).serialize(), // get the form data
            type: $(this).attr('method'), // GET or POST
            url: $(this).attr('action'), // the file to call
            success: function(response) { // on success..
                var data = $.parseHTML( response );
                $(response).printThis();
            }
        });
        return false;
    });
});
