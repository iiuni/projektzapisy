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
