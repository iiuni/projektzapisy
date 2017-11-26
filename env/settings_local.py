DEBUG = True
TEMPLATE_DEBUG = True
PIPELINE = False
ALLOWED_HOSTS = ['*']
DATABASES = {
     'default' : {
        'ENGINE' : 'django.db.backends.postgresql_psycopg2',
            'NAME' : 'fereol',
            'PORT' : '5432',
            'USER' : 'fereol',
            'PASSWORD' : 'fereolpass',
            'HOST' : 'localhost',
            'CHARSET' : 'utf8',
            'USE_UNICODE' : True,
        } 
}
