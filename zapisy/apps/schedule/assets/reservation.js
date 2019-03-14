import "./reservation.css";

import "jquery";
const $ = jQuery;

// przejdz do danego elementu
var scroll = function(id) {
    $('html, body').animate({
        scrollTop: $(id).offset().top
    }, 0);
};

// wyczyść formularz dodawania terminu
var resetAddTermForm = function() {
    $('#hiddenroom').val('');
    $('#inputplace').val('');
    $('#addterm').text('Dodaj termin');
};

// sprawdź poprawność dodawanego terminu
var validateAddTermForm = function() {
    let valid = $('#addtermform')[0].checkValidity();
    let begin = $('#begin');
    let end = $('#end'); 
    if( begin.val() > end.val() ) {
        valid = false;
        begin.addClass('is-invalid');
        end.addClass('is-invalid');
    }
    else{
        begin.removeClass('is-invalid');
        end.removeClass('is-invalid');
    }
    let location = $('#location');
    if( location.val().length == 0 ){
        valid = false;
        location.addClass('is-invalid');
    }
    else
        location.removeClass('is-invalid');
    return valid;
};


$(document).ready(() => {

    // dodawanie terminu do listy
    $('#addtermform').submit((event) => {
        event.preventDefault();

        if( !validateAddTermForm() ){
            return false;
        }

        let isNew = false;
        if ($('#hiddenid').val()) {
            var counter = parseInt($('#hiddenid').val());
        } else {
            isNew = true;
            var counter = parseInt($('input[name="term_set-TOTAL_FORMS"]').val());
        }

        let namePrefix = 'term_set-'+ counter +'-';
        let template = $('.termstable-template'); 
        let tr = template.clone(true).removeClass("termstable-template d-none");
        let value;
        
        value = $('#term').val();
        tr.find('.termstable-template-term > strong').append(value);
        tr.find('.termstable-template-term > input')
            .attr('name', namePrefix + 'day').val(value);

        value = $('#begin').val();
        tr.children('.termstable-template-begin').append(value);
        tr.find('.termstable-template-begin > input')
            .attr('name', namePrefix + 'start').val(value);

        value = $('#end').val();
        tr.children('.termstable-template-end').append(value);
        tr.find('.termstable-template-end > input')
            .attr('name', namePrefix + 'end').val(value);

        value = $('#location').val();
        tr.children('.termstable-template-location').append(value);
        tr.find('.termstable-template-location > .termstable-template-place')
            .attr('name', namePrefix + 'place').val(value);
        tr.find('.termstable-template-location > .termstable-template-room')
            .attr('name', namePrefix + 'room').val($("#hiddenroom").val());

        if ( !isNew && $('#termstable tbody tr').eq(counter).find('input[name$="-id"]').length > 0) {
            tr.append($('#termstable tbody tr').eq(counter).find('input[name$="-id"]').clone(true));
        }

        tr.find(".termstable-template-delete")
            .attr('name', namePrefix + 'DELETE')
            .attr('id', 'id_' + namePrefix + 'DELETE');

        if ( !isNew ) {
            let old = $('#termstable tbody tr').eq(counter);
            tr.insertAfter(old);
            old.remove();
        } else {
            tr.insertBefore(template);
            $('input[name="term_set-TOTAL_FORMS"]').val(parseInt(counter) + 1);
        }


        resetAddTermForm();
        return false;
    });

    // rozpoczęcie edycji istniejącego terminu
    $('.editterm').click((event) => {
        event.preventDefault();

        let tr = $(event.target).parent().parent().addClass('edited bg-light');
        let room = tr.find('input[name$="-room"]').val();
        $('#addterm').text('Zmień termin');
        $('#term').val(tr.find('input[name$="-day"]').val()).change();
        $('#begin').val(tr.find('input[name$="-start"]').val());
        $('#end').val(tr.find('input[name$="-end"]').val());
        $('#location').val(tr.find('input[name$="-place"]').val());

        $('#hiddenroom').val(room);
        $('#hiddenid').val(tr.index());

        if("" === room) {
            $('#inputplace').val($('#location').val());
        }

       scroll('#addtermform');
    });

    // zapisz formularz
    $('#save_event').click((event) => {
        if ($('#termstable tbody').find('tr:not(.removed, .d-none)').length == 0 ) {
            if (window.confirm("Czy na pewno chcesz usunąć to wydarzenie?"))
                $('#mainform').submit();                          
        } else {
            $('#mainform').submit();
        }
    });

    // ustaw ignorowanie konfliktów
    $('#ignore_all_conflicts').change((event) => {
        let checked = event.target.checked;
        $('input[name$="-ignore_conflicts"]').val(+checked);
    });

    // ustaw zewnętrzną lokalizację
    $('#addoutsidelocation').click((event) => {
        $('#hiddenroom').val('');
        $('#location').val($('#inputplace').val());
        scroll('#location');
    });

    // ustaw termin w stan do usunięcia
    $('.removeterm').click((event) => {
        var tr = $(event.target).parent().parent();
        tr.find('input[name$="-DELETE"]').prop('checked', true);
        tr.find('.unremoveterm').removeClass('d-none');
        tr.find('.editterm').addClass('d-none');
        tr.addClass('removed text-danger');
        $(event.target).addClass('d-none');
    })

    // anuluj ustawienie terminu w stan do usunięcia
    $('.unremoveterm').click((event) => {
        var tr = $(event.target).parent().parent();
        tr.find('input[name$="-DELETE"]').prop('checked', false);
        tr.find('.removeterm').removeClass('d-none');
        tr.find('.editterm').removeClass('d-none');
        tr.removeClass('removed text-danger');
        $(event.target).addClass('d-none');
    });
});