"""
Django settings for ocatsite project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""


# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
import socket
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'ocatsite/static'),
    os.path.join(BASE_DIR, 'ocatsite/site_static'),
)

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
with open('/data/mta4/CUS/www/Usint/Ocat/ocatsite/static/safe/skey') as f:
    SECRET_KEY = f.read().strip()

# SECURITY WARNING: don't run with debug turned on in production!

if socket.gethostname() == 'ars':
    DEBUG = True
    TEMPLATE_DEBUG = True
    ALLOWED_HOSTS = []
else:
    DEBUG = False
    TEMPLATE_DEBUG = False
    ALLOWED_HOSTS = ['https://cxc.cfa.harvard.edu/']
    CSRF_COOKIE_SECURE = True
    SESSION_COOKIE_SECURE = True


# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'utils',
    'ocatmain',
    'ocatdatapage', 
    'chkupdata',
    'orupdate', 
    'rm_submission',
    'ocat_express', 
    'updated',
    'schedule_submitter',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.RemoteUserMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

PASSWORD_HASHERS = (
#    'django.contrib.auth.hashers.BCryptPasswordHasher',
    'django.contrib.auth.hashers.MD5PasswordHasher',
    'django.contrib.auth.hashers.CryptPasswordHasher',
    'django.contrib.auth.hashers.BCryptSHA256PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher',
    'django.contrib.auth.hashers.SHA1PasswordHasher',
)


AUTHENTICATION_BACKENDS = (
    'utils.backend.SettingBackend',
#    'django.contrib.auth.backends.ModelBackend',
#    'django.contrib.auth.backends.RemoteUserBackend',
)
#
#--- admin user new field realted; see ocatdatapage models.py and admin.py
#
AUTH_PROFILE_MODULE = 'ocatdatapage.UserProfile'

SESSION_SERIALIZER = 'django.contrib.sessions.serializers.PickleSerializer'

ROOT_URLCONF = 'ocatsite.urls'

WSGI_APPLICATION = 'ocatsite.wsgi.application'

TEMPLATE_DIRS = (
#    '/data/mta4/CUS/www/Usint/Ocat/ocatsite/templates',
    os.path.join(BASE_DIR, 'templates'),
    os.path.join(os.path.dirname(__file__), 'templates').replace('\\', '/'),
)


# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'OPTIONS': { 
                    'read_default_file': os.path.join(BASE_DIR, 'ocatsite/ocat.cnf'),
                   },
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/

STATIC_URL = '/static/'

#
# admin/manager
#
ADMINS = (
    ('Takashi Isobe', 'tisobe@cfa.harvard.edu'),
)
MANAGERS = (
    ('Takashi Isobe', 'tisobe@cfa.harvard.edu'),
)
