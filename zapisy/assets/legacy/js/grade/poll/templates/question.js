var question = "<div class='clearfix poll-question-answer'>"+

"<div class='input'>"+
"	<input type='text' class='question-answer autocomplete required' id='poll[question][${id}][answers][${size}]' name='poll[question][${id}][answers][]' value='${name}'>"+
"	{{if leading === true }}"+
"	<label class='hideOnCheckbox' style='display:inline' for='poll[question][${id}][answers][${size}]'><input type='checkbox' style='display:inline' class='hideOnCheckbox' id='poll[question][${id}][hideOn][${size}]' name='poll[question][${id}][hideOn][]' value='${size}'>Ukryj sekcję</label>{{/if}}"+
"	<img src='/static/images/remove-ico.png' class='remove' alt='usuń'>"+
"</div>"+
"</div>"

$.template( "question", question );
