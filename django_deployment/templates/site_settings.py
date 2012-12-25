DEBUG = %(DEBUG)s
TEMPLATE_DEBUG = DEBUG

DATABASES = {
    'default': {
        'ENGINE': '%(database.ENGINE)s',
        'NAME': '%(database.NAME)s',
        'USER': '%(database.USER)s',
        'PASSWORD': '%(database.PASSWORD)s',
        'HOST': '%(database.HOST)s',
        'PORT': '%(database.PORT)s',
    }
}

CACHES = {
    'default': {
        'BACKEND': '%(cache.BACKEND)s',
        'LOCATION': '%(cache.LOCATION)s',
        'TIMEOUT': %(cache.TIMEOUT)i,
        'KEY_PREFIX': '%(cache.KEY_PREFIX)s',
    }
}

# Make this unique, and don't share it with anybody
SECRET_KEY = '%(SECRET_KEY)s'

DOMAIN = '%(DOMAIN)s'
URL_PREFIX = '%(URL_PREFIX)s'

STATIC_ROOT = '%(STATIC_ROOT)s'

# Emails
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = '%(from_email)s'
EMAIL_HOST_PASSWORD = '' # TODO: set it

DEFAULT_FROM_EMAIL = '%(from_email)s'
SERVER_EMAIL = '%(from_email)s'
