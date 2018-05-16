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
import re
#-------
from os.path import join, dirname, realpath
os.environ.setdefault('SKA', '/proj/sot/ska')
#-------
#import MySQLdb

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
    ALLOWED_HOSTS = ['http://127.0.0.1:8000/']
else:
    DEBUG = False
    TEMPLATE_DEBUG = False
    ALLOWED_HOSTS = ['http://r2d2-v.cfa.harvard.edu/']
    CSRF_COOKIE_SECURE = True
    SESSION_COOKIE_SECURE = True

path = join(BASE_DIR, 'ocatsite/static/dir_list_py')
f    = open(path, 'r')
data = [line.strip() for line in f.readlines()]
f.close()
#
#--- read a few params
#
for ent in data:
    atemp = re.split('::', ent)
    var  = atemp[1].strip()
    line = atemp[0].strip()
    exec "%s = %s" %(var, line)

line       = l_path + '.htmysqlserver'
f          = open(line, 'r')
sql_server = f.readline().strip()
f.close()

line       = l_path + '.htsqlwebpass'
f          = open(line, 'r')
cuspass    = f.readline().strip()
f.close()

line       = l_path + '.hdbname'
f          = open(line, 'r')
dbname     = f.readline().strip()
f.close()



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
    'django.contrib.auth.backends.ModelBackend',
    'django.contrib.auth.backends.RemoteUserBackend',
    'utils.backend.SettingBackend',
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
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'ocatsite/db.sqlite3'),
    }
}

#DATABASES = {
#    'default': {
#        'ENGINE':   'django.db.backends.mysql', 
#        'NAME':     dbname,
#        'USER':     'cusweb',
#        'PASSWORD': cuspass,
#        'HOST': '   r2d2-v.cfa.harvard.edu',   # Or an IP Address that your DB is hosted on
#        'PORT':     '3306',
#    }
#}


# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'en_US.UTF-8'

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
