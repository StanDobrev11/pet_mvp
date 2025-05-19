from pet_mvp.settings import *

# Disable modeltranslation for tests
INSTALLED_APPS = [app for app in INSTALLED_APPS if app != 'modeltranslation']

# Use in-memory SQLite database for testing
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}