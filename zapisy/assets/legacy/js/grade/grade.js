

FormGenerator = Object();

FormGenerator.init = function()
{
	FormGenerator.questions = 0;
        FormGenerator.form      = $("#poll-form");
	$("#add-question").click ( function(event){
        event.preventDefault();
		FormGenerator.addQuestion(); }
	)
}

FormGenerator.addQuestion = function()
{
	FormGenerator.questions++;

	var question_type = $("#add-question-type").val();

	var type = document.createElement('input');
	    type.type = 'hidden'
	    type.value = question_type;
	    type.name = 'poll[' + FormGenerator.questions + '][type]';
	
	var title = document.createElement('input');
	    title.type = 'text';
            title.name = 'poll[' + FormGenerator.questions + '][title]';
	    title.value = 'Wpisz pytanie';
	if (question_type != 'open')
	{	
		var ul = document.createElement('ul');
		    ul.id = 'Question' + FormGenerator.questions;
		    ul.className = 'poll-question-answers';

		liAnswer = document.createElement('li');
		liAnswer.className = 'poll-question-answer';

		var answer = document.createElement('input');
		    title.type = 'text';
		    answer.name =  'poll[' + FormGenerator.questions + '][answers][]';
		    answer.value = 'odpowiedź';

		$(liAnswer).append (answer);
		$(ul).append (liAnswer);
	}
	var ok =  document.createElement('input');
	    ok.type = 'button';
	    ok.value = 'dodaj odpowiedź';
	var number = FormGenerator.questions;
	  $(ok).click(function(){FormGenerator.addOption ( number )}); 

	var li = document.createElement('li');
	    li.className = "poll-question";

	$(li).append (type);
	$(li).append (title);
	if (question_type != 'open') { $(li).append (ul);
	$(li).append (ok);}
	FormGenerator.form.append (li);
	
}

FormGenerator.addOption = function( question )
{
	var li = document.createElement('li');
        li.className = 'poll-question-answer';
	var answer = document.createElement('input');
	    answer.name =  'poll[' + question + '][answers][]';
	    answer.value = 'odpowiedź';
	$(li).append(answer);
	$('#Question' + question).append(li);
}

$(FormGenerator.init);


