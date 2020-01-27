import "jquery";
const $ = jQuery;


$(document).ready(() => {
    // zaznacz wszystkie sale do raportu
    $('#select-all-button').click((event) => {
        $('#id_rooms option').prop('selected', true);    
    });

    //Wydrukuj zawartość strony
    $('.print-report').click((event) => {
        window.print();  
    });

    $('#id_rooms').addClass('form-control');
    $('#id_weeks').addClass('form-control');

});