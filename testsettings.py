import django

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    },
}

INSTALLED_APPS = (
    'vanilla',
)

if django.VERSION >= (1, 10):
    MIDDLEWARE = [
        'django.middleware.common.CommonMiddleware',
        'django.middleware.csrf.CsrfViewMiddleware',
    ]
else:
    MIDDLEWARE_CLASSES = [
        'django.middleware.common.CommonMiddleware',
        'django.middleware.csrf.CsrfViewMiddleware',
    ]

SECRET_KEY = 'abcde12345'
