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
}
