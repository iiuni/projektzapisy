var data = {}

function recompute() {
	var sum = 0;
	$('table#hours-table td input:not(:hidden)').each(function(){
	        val = parseInt($(this).val(),10);
	        if (!isNaN(val))
	        	sum += val;
	});
	shouldbe = parseInt($('#hours_should_be').html(),10);
	color = '#00FF00';
	$(':button[type="submit"]').removeAttr("disabled");
	if (Math.abs(shouldbe-sum)>20) {
		color = '#FF0000';
 		$(':button[type="submit"]').attr("disabled", true);
	}
	$('#target_sum').html('<span style="color:'+color+'">'+sum+'</span>');
}

$(function() {
	$('tr.dynamic-formset').formset({
		'removed': function() {
			recompute();
		}
	});

	$('select#id_entity-type').change(function() {
		for (var key in data[$(this).val()]) {
			if (key=='default_ects') {
				new_ects = data[$(this).val()][key];
				$('#id_entity-ects').val(new_ects);
				$('#hours_should_be').html(new_ects*25)
			} else
			{
				if (data[$(this).val()][key]) {
					$('#id_entity-'+key).val(30);
				} else {
					$('#id_entity-'+key).val('');
				}
			}
		}
		recompute();
		$('html, body').animate({
		        scrollTop: $("#hours-table").offset().top
		    }, 1000);
	});

	$('table#hours-table input').live('change', function() {
		recompute();
	});

	$("tr:has(ul.errorlist)").addClass("haserrors");

	recompute();
})

function proposal_init(types_data) {
	data = types_data;
}


function beforeSubmitButton(nameEditPlID,nameEditEnID) 
{ 
    var namePL = document.getElementById(nameEditPlID);
    var nameEN = document.getElementById(nameEditEnID);
    
    if (namePL.value=="") namePL.value=nameEN.value;
    //if (nameEN.value=="") nameEN.value=namePL.value;

    var listRows = document.querySelectorAll('[id^="id_studentwork_set-"]');

    for ( var i = listRows.length-1; i>=0 ; i-- ) {
        //id_studentwork_set-2-hours
        var idString = listRows[i].id;

        if (idString.indexOf('id_studentwork_set')==0)
        if (idString.indexOf('-hours')!=-1)
        if (listRows[i].value=="" || listRows[i].value=="0")
        {
           // listRows[i].parentElement.parentElement.remove();    
			listRows[i].parentElement.getElementsByClassName("delete-row")[0].click();
		
			//parentElement.click();        
        }
    }
}