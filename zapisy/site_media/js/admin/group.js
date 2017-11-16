var $ = django.jQuery;

var send_post = function(url, items){
        var i, theForm, newInput;

        theForm = document.createElement('form');
        theForm.action = url;
        theForm.method = 'post';

        for (i in items) {
            if (items.hasOwnProperty(i)) {
                newInput = document.createElement('input');
                newInput.type = 'hidden';
                newInput.name = i;
                newInput.value = items[i];
                theForm.appendChild(newInput);
            }
        }

        newInput = document.createElement('input');
        newInput.type = 'hidden';
        newInput.name = 'csrfmiddlewaretoken';
        newInput.value = $('input[name="csrfmiddlewaretoken"]').val();
        theForm.appendChild(newInput);
        document.getElementById('hidden_form_container').appendChild(theForm);
        theForm.submit();
    };

$(document).ready(function () {
    var group = $('.field-id div p').text();
    $('.field-limit').find('p').append("" +
       "<label style='float:right'>Zmień limit na: <input type='text' name='new_limit' id='new_limit'><button id='change_group_limit'>Zmień</button></label><div id='hidden_form_container' style='display:hidden'></div>");
    $('#change_group_limit').click(function (event) {
        event.preventDefault();
        var limit = $('#new_limit').val();
        if (!limit || !group) {
            return;
        }
        send_post('/fereol_admin/courses/group/change_limit/', {
            'limit': limit,
            'group_id': group
        });

    });

    $('tr[id^="record_set"]').each(function () {
        var status = $(this).find('.status p').text(),
            recordid = $(this).find('.id p').text();

        if(status === 'zapisany') {
            $(this).append('<button class="fire">Wypisz</button>');
            $(this).find('.fire').click(function (event) {
                event.preventDefault();
                var c = confirm("Na pewno usunąć studenta z grupy?");
                if (c) {
                    send_post('/fereol_admin/courses/group/remove_student/', {
                        'recordid': recordid,
                        'group_id': group
                    });
                }
            })
        }
    });

    $('#record_set-group .add-row').remove();

    $('#record_set-group').append('<button class="add_student">Zapisz osobę</button>');
    $('#record_set-group .add_student').click(function(event){
        event.preventDefault();
        var button = $(this);
        button.hide();
        $('#record_set-group table tbody').append('<tr class="dynamic-record_set row1""><td class="original"><input type="hidden" name="set-id" id="set-id"><input type="hidden" name="set-group" value="11232" id="set-group"></td><td class="student">' +
            '<input class="vForeignKeyRawIdAdminField" type="text" name="set-student" id="set-student">' +
            '<a href="/fereol_admin/users/student/?_to_field=id" class="related-lookup" id="lookup_set-student" onclick="return showRelatedObjectLookupPopup(this);">' +
            '<img src="/static/admin/img/selector-search.gif" width="16" height="16" alt="Szukaj"></a></td><td><button class="save_new_student">Zapisz</button></td></tr>');
        $('.save_new_student').click(function(event){
            event.preventDefault();
            var student = $('#record_set-group').find('#set-student').val();

            send_post('/fereol_admin/courses/group/add_student/', {
                'student': student,
                'group_id': group
            });
            button.show();
            $(this).parent().parent().remove();
        })
    })
});