PIPELINE_CSS = {
    'main': {
        'source_filenames': (
            'css/main.css',
            'css/fereol.css',
        ),
        'output_filename': 'css/main.min.css',
        'extra_context': {
            'media': 'screen,projection',
        },
    },
    'ticketssave': {
        'source_filenames': (
            'css/main.css',
            'css/fereol.css',
            'css/grade/tickets_save.css'
        ),
        'output_filename': 'css/ticketssave.min.css',
        'extra_context': {
            'media': 'screen,projection',
        },
    },
    'connectionchoice': {
        'source_filenames': (
            'css/main.css',
            'css/fereol.css',
            'css/grade/connections_choice.css',
            'css/ui-progressbar.css'
        ),
        'output_filename': 'css/connectionchoice.min.css',
        'extra_context': {
            'media': 'screen,projection',
        },
    },
    'gradebase': {
        'source_filenames': (
            'css/main.css',
            'css/fereol.css',
            'css/common/mainPage.css',
            'css/grade/poll.css',
            'css/grade/results.css',
            'css/grade/answer.css',
            'css/ui-progressbar.css',
        ),
        'output_filename': 'css/gradebase.min.css',
        'extra_context': {
            'media': 'screen,projection',
        },
    },
    'gradepollshow': {
        'source_filenames': (
            'css/main.css',
            'css/fereol.css',
            'css/grade/declaration.css'
        ),
        'output_filename': 'css/gradepollshow.min.css',
        'extra_context': {
            'media': 'screen,projection',
        },
    },
    'help': {
        'source_filenames': (
            'css/main.css',
            'css/fereol.css',
            'css/help.css',
        ),
        'output_filename': 'css/help.min.css',
        'extra_context': {
            'media': 'screen,projection',
        },
    },
    'login': {
        'source_filenames': (
            'css/main.css',
            'css/fereol.css',
            'css/common/login.css'
        ),
        'output_filename': 'css/login.min.css',
        'extra_context': {
            'media': 'screen,projection',
        },
    },
    'userslist': {
        'source_filenames': (
            'css/main.css',
            'css/fereol.css',
            'css/enrollment/courses.css',
            'css/common/schedule.css',
            'css/common/schedule-courses.css',
            'css/enrollment/users/users-list.css'
        ),
        'output_filename': 'css/userslist.min.css',
        'extra_context': {
            'media': 'screen,projection',
        },
    },
}

PIPELINE_JS = {
    'main': {
        'source_filenames': (
            'js/jquery/jquery-1.5.2.js',
            'js/jquery/jquery-ui-1.8.17.custom.js',
            'js/jquery/jquery.cookies.2.2.0.min.js',
            'js/jquery/baseExtensions.js',
            'js/main.js',
            'js/common/bootstrap-dropdown.js',
        ),
        'output_filename': 'js/main.min.js',
    },
    'connectionchoice': {
        'source_filenames': (
            'js/jquery/jquery-1.5.2.js',
            'js/jquery/jquery-ui-1.8.17.custom.js',
            'js/jquery/jquery.cookies.2.2.0.min.js',
            'js/jquery/baseExtensions.js',
            'js/main.js',
            'js/common/bootstrap-dropdown.js',
            'js/jquery/tooltip.jquery.js',
            'js/grade/ticket_create/BigInt.js',
            'js/grade/ticket_create/ticket_create.js',
        ),
        'output_filename': 'js/connectionchoice.min.js',
    },
    'keysgenerate': {
        'source_filenames': (
            'js/jquery/jquery-1.5.2.js',
            'js/jquery/jquery-ui-1.8.17.custom.js',
            'js/jquery/jquery.cookies.2.2.0.min.js',
            'js/jquery/baseExtensions.js',
            'js/main.js',
            'js/common/bootstrap-dropdown.js',
            'js/grade/ticket_create/keys_generate.js'
        ),
        'output_filename': 'js/keysgenerate.min.js',
    },
    'pollresult': {
        'source_filenames': (
            'js/jquery/jquery-1.5.2.js',
            'js/jquery/jquery-ui-1.8.17.custom.js',
            'js/jquery/jquery.cookies.2.2.0.min.js',
            'js/jquery/baseExtensions.js',
            'js/main.js',
            'js/common/bootstrap-dropdown.js',
            'js/grade/poll/poll_results.js',
        ),
        'output_filename': 'js/pollresult.min.js',
    },
    'employeelist': {
        'source_filenames': (
            'js/jquery/jquery-1.5.2.js',
            'js/jquery/jquery-ui-1.8.17.custom.js',
            'js/jquery/jquery.cookies.2.2.0.min.js',
            'js/jquery/baseExtensions.js',
            'js/main.js',
            'js/common/utils.js',
            'js/common/bootstrap-dropdown.js',
            'js/jquery/jquery-tmpl/jquery.tmpl.min.js',
            'js/components/sidebar.js',
            'js/common/listFilter.js',
            'js/enrollment/users/templates/employee.js',
            'js/enrollment/users/employees-list.js',
        ),
        'output_filename': 'js/employeelist.min.js',
    },
    'studentlist': {
        'source_filenames': (
            'js/jquery/jquery-1.5.2.js',
            'js/jquery/jquery-ui-1.8.17.custom.js',
            'js/jquery/jquery.cookies.2.2.0.min.js',
            'js/jquery/baseExtensions.js',
            'js/main.js',
            'js/common/utils.js',
            'js/common/bootstrap-dropdown.js',
            'js/jquery/jquery-tmpl/jquery.tmpl.min.js',
            'js/components/sidebar.js',
            'js/common/listFilter.js',
            'js/enrollment/users/templates/student.js',
            'js/enrollment/users/students-list.js',
        ),
        'output_filename': 'js/studentlist.min.js',
    },
}
