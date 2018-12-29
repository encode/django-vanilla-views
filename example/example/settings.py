import django
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DEBUG = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'sqlite3.db',
    }
}

STATIC_URL = '/static/'

STATICFILES_DIRS = [
    'statics',
]

SECRET_KEY = 'not-secret'

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

ROOT_URLCONF = 'example.urls'

WSGI_APPLICATION = 'example.wsgi.application'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
    },
]

INSTALLED_APPS = [
    'django.contrib.staticfiles',
    'example.notes',
]
