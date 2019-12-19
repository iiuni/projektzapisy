import "jquery";
import "./report.css";
const $ = jQuery;


$(document).ready(() => {
    // zaznacz wszystkie sale do raportu
    $('#select-all-button').click((event) => {
        $('#id_rooms option').prop('selected', true);    
    });

    // przygotuj raport do wydruku
    $('#reportForm').submit(function() {
        $.ajax({
            data: $(this).serialize(),
            type: $(this).attr('method'),
            url: $(this).attr('action'),
            success: function(response) {
                $('#report-preview').html(response);
            }
        });
        return false;
    });

    //Wydrukuj zawartość strony
    $('#print').click((event) => {
        window.print();  
    });

    $('#id_rooms').addClass('form-control');

});