"""
Django settings for Online_Exam project.

Generated by 'django-admin startproject' using Django 1.8.14.

For more information on this file, see
https://docs.djangoproject.com/en/1.8/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.8/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.8/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'yftv^g7w17v-vd96!=ad37dv@m$_gh^nn_&d*4@qzsoce5*pd3'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'alcpt',
    'captcha',
    'django_plotly_dash.apps.DjangoPlotlyDashConfig',
    'django_crontab', #工作排程
    'dbbackup',#資料庫備份
)

CRONJOBS = [
    ('*/1 * * * *', 'alcpt.cron.backup','>>/home/max/Desktop/crontab.log')  
]

#備份路徑,記得設定為自己的路徑
DBBACKUP_STORAGE = 'django.core.files.storage.FileSystemStorage'
DBBACKUP_STORAGE_OPTIONS = {'location': '/home/max/Desktop/ALCPT/backup_files'}
#備份主設定


MIDDLEWARE = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    # 'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    # 'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
)

ROOT_URLCONF = 'Online_Exam.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.jinja2.Jinja2',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.i18n',
            ],
            'autoescape':
            True,
            'environment':
            'alcpt.jinja2.environment',
        }
    },
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'Online_Exam.wsgi.application'

# Database
# https://docs.djangoproject.com/en/1.8/ref/settings/#databases

# mysql
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'alcpt',
        'USER': 'root',
        'PASSWORD': 'alcptalcpt',
        'HOST': '127.0.0.1',
        'PORT': '3306',
    }
}

CAPTCHA_NOISE_FUNCTIONS = (
    'captcha.helpers.noise_null',  # 沒有樣式
    # 'captcha.helpers.noise_arcs',   # 線
    'captcha.helpers.noise_dots',  # 點
)

# CAPTCHA_IMAGE_SIZE = (150, 200)    # 驗證碼圖片大小

CAPTCHA_BACKGROUND_COLOR = 'white'  # 驗證碼顏色

# CAPTCHA_CHALLENGE_FUNCT = 'captcha.helpers.math_challenge' 數學計算式驗證碼

# CAPTCHA_TIMEOUT = 0.1 驗證碼限制時間

# CAPTCHA_LENGTH = 1 #驗證碼長度

# Internationalization
# https://docs.djangoproject.com/en/1.8/topics/i18n/

TIME_ZONE = 'Asia/Taipei'

# 國際化
USE_I18N = True

USE_L10N = True

#USE_TZ = True

LANGUAGES = {
    ('en-us', 'English'),
    ('zh', '中文繁體'),
}
LANGUAGE_CODE = 'zh-Hant'  # 'en-us'
LOCALE_PATHS = [
    os.path.join(BASE_DIR, 'locale'),
]

STATIC_URL = '/static/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]
STATIC_ROOT = os.path.join(BASE_DIR, 'alcpt/static')
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media/')

LOGIN_REDIRECT_URL = '/proclamation'
LOGOUT_REDIRECT_URL = '/'

AUTH_USER_MODEL = 'alcpt.User'

ALLOWED_HOSTS = ['*']
