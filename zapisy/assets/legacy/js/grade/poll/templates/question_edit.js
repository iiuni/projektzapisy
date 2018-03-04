var question_edit = "<li class='poll-question'>                         " +
    "	<input type='hidden' name='poll[question][order][]' value='${id}'>  " +
    "	<div class='section-edit section-mouseover'>                        " +
    "	    " +
    "	" +
    "	<formset>" +
    "	" +
    "	        <div class='clearfix'>" +
    "	            <label for='poll[question][${id}][title]'>Podaj treść pytania</label>" +
    "	    " +
    "	                    <div class='input'>" +
    "	                        <input type='text' id='poll[question][${id}][title]' name='poll[question][${id}][title]' class='required'>" +
    "	                    </div>" +
    "	        </div>" +
    "	        <div class='clearfix'>" +
    "	            <label for='poll[question][${id}][description]'>Opis pytania</label>" +
    "	        " +
    "	                    <div class='input'>" +
    "	                        <input type='text' id='poll[question][${id}][description]' name='poll[question][${id}][description]' class='section-option'>" +
    "	                    </div>" +
    "	        </div>" +
    "	        <div class='clearfix typeSelectDiv'>" +
    "	            <label for='poll[question][${id}][formtype]'>Typ pytania</label>" +
    "" +
    "	                <div class='input'>" +
    "	                    <input type='hidden' name='poll[question][${id}][type]' value='open'>" +
    "	                <select id='poll[question][${id}][formtype]' name='poll[question][${id}][formtype]' class='typeSelect options'>" +
    "	     				    </select>" +
    "	                    </div>" +
    "	        </div>" +
    "	</formset>" +
    "	<input type='hidden' name='fake' class='fake-answerser anyanswer'>" +
    "	<formset class='answerset ui-sortable' style=''></formset>" +
    "	<formset class='optionset'>" +
    "	        <div class='clearfix isScale option' style='display: none;'>" +
    "			<label for='poll[question][${id}][isScale]'>Pytanie w formie skali</label>" +
    "	                    <div class='input'>" +
    "               			<input type='checkbox' id='poll[question][${id}][isScale]' class='scale' name='poll[question][${id}][isScale]'>" +
    "	                    </div>" +
    "	        </div>" +
    "	        <div class='clearfix choiceLimit option' style='display: none;'>" +
    "	            <label for='poll[question][${id}][choiceLimit]'>Limit odpowiedzi</label>" +
    "	                    <div class='input'>" +
    "                          <select id='poll[question][${id}][choiceLimit]' name='poll[question][${id}][choiceLimit]'>"+
    "                            <option value='0'>Brak limitu</option>"+
    "                          </select>"+
    "	                    </div>" +
    "	        </div>" +
    "	        <div class='clearfix hasOther option' style='display: none;'>" +
    "	            <label for='poll[question][${id}][hasOther]'>Odpowiedź inne</label>" +
    "	                    <div class='input'>" +
    "                          <input type='checkbox' id='poll[question][${id}][hasOther]' name='poll[question][${id}][hasOther]'>"+
    "	                    </div>" +
    "	        </div>" +
    "	</formset>" +
    "	<formset>" +
    "    <div class='clearfix'>" +
    "	  <button class='ready btn success' type='button'>Gotowe</button>" +
    "     <button class='delete btn' type='button'>Usuń</button>" +
    "	</div>" +
    "	</formset>" +
    "	</div>" +
    "</li>"

$.template( "question_edit", question_edit );
