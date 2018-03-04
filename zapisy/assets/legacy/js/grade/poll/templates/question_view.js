var question_view = "" +
"<div class='fieldWrapper section-show poll-section-field{{if optionset.is_leading }} poll-section-leading{{/if}}'>" +
"   <input class='edit-mode' type='button' value='Edytuj'>" +
"            <h4>${title}</h4> " +
"            {{if isdesc>0 }}<span class='poll-section-description'>${desc}</span>{{/if}}" +
"       {{if optionset.choiceLimit>0 }}" +
"    <span class='poll-section-description'>Możesz zaznaczyć maksymalnie ${optionset.choiceLimit} odpowiedzi</span>" +
"       {{/if}}"+
"	{{if type === 'single' }}" +
"        <ul class='poll-section-answer-list{{if optionset.isScale}} scale{{/if}}'>" +
"	{{each(i, question) questionset}}	" +
"            <li  class='poll-section-answer-item'>" +
"                <input type='radio' id='${question.id}' class='poll-section-radio{{if question.isHiden }} poll-section-radio-hideon{{else}} poll-section-radio-all{{/if}}' disabled='disabled' >" +
"                <label for='${question.id}'>${question.title}</label>" +
"            </li>" +
"	{{/each}}" +
"        </ul>" +
" {{if optionset.isScale}} <div class='clear'></div>{{/if}} " +
"	{{/if}}" +
"	{{if type === 'multi' }}" +
"                <ul class='poll-section-answer-list{{if optionset.choiceLimit>0 }} poll-section-choicelimit{{/if}}'>"+
"	{{each(i, question) questionset}}	" +
"                    <li  class='poll-section-answer-item'><input type='checkbox' class='poll-section-choice{{if optionset.choiceLimit>0 }} poll-section-choicelimit-choice{{/if}}' id='${question.id}' disabled='disabled'>" +
"                    <label for='${question.id}'>${question.title}</label>" +
"                    {{if question.title == 'Inne' }}" +
"                        <input type='text' disabled='disabled' class='poll-section-other{{if optionset.choiceLimit>0 }} poll-section-choicelimit-choice{{/if}}'>" +
"                    {{/if}}" +
"                    </li>" +
"	{{/each}}" +
"                </ul>" +
"	{{/if}}" +
"	{{if type === 'open'}}" +
"                <textarea cols='40' rows='5' disabled='disabled'></textarea>" +
"	{{/if}}" +
"        </div>";




$.template( "question_view", question_view );