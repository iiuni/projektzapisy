/**
 * Created by mjablonski
 * User: iks
 * Date: 21.03.11
 * Time: 08:00
 * To change this template use File | Settings | File Templates.
 */


var poll_types = new Object();

/*
*
* type        - type used only in creator, must be unique
* realtype    - type of question in database, open|single|multi
* name        - name used in select
* haveAnswers - true | false
* answers     - default answers add during change types
* options     - list of options show during change types
* optionsOn   - list of options default checked
 */

poll_types['open'] = {
    type:        'open',
    realtype:    'open',
    name:        'Pytanie otwarte',
    haveAnswers: false,
    options:   [],
    optionsOn: []
};

poll_types['single'] = {
    type: 'single',
    realtype: 'single',
    name: 'Pytanie jednokrotnego wyboru',
    haveAnswers: true,
    answers: [],
    options: ['isScale'],
    optionOn: []
};

poll_types['multi'] = {
    type: 'multi',
    realtype: 'multi',
    name: 'Pytanie wielokrotnego wyboru',
    haveAnswers: true,
    answers: [],
    options: ['choiceLimit', 'hasOther'],
    optionOn: []
};

poll_types['yes_no'] = {
    type: 'yes_no',
    realtype: 'single',
    name: 'Pytanie tak/nie',
    haveAnswers: true,
    answers: ['tak', 'nie'],
    options: ['isScale'],
    optionOn: []
};

poll_types['scale5'] = {
    type: 'scale5',
    realtype: 'single',
    name: 'Pytanie w formie skali(1-5)',
    haveAnswers: true,
    answers: ['1', '2', '3', '4', '5'],
    options: ['isScale'],
    optionOn: ['scale']
};


poll_types['scaled'] = {
    type: 'scaled',
    realtype: 'single',
    name: 'Skala opisowa',
    haveAnswers: true,
    answers: ['zdecydowanie tak', 'raczej tak', 'trudno powiedzieć', 'raczej nie', 'zdecydowanie nie'],
    options: ['isScale'],
    optionOn: ['scale']
};

poll_types['scalep'] = {
    type:'scalep',
    realtype:'single',
    name:'Skala - liczba godzin',
    haveAnswers:true,
    answers:['Regularnie (do 4 nieobecności)', 'Nieregularnie (5-9 nieobecności)', 'Rzadko (10-14 nieobecności)', 'Wcale'],
    options:['isScale'],
    optionOn:['scale']
};

poll_types['scalew'] = {
    type: 'scalew',
    realtype: 'single',
    name: 'Skala - nakład pracy',
    haveAnswers: true,
    answers: ['Wcale', 'Mniej niż 1 godz.', 'około 2 godz.', 'około 4 godz.', 'Więcej niż 6 godz.'],
    options: ['isScale'],
    optionOn: ['scale']
};
