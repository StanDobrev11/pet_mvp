# Language Switcher Implementation

This document describes the implementation of a language switcher in the navbar using SVG flag icons.

## Changes Made

1. Added SVG flags (bg-flag.svg and uk-flag.svg) to the navbar
2. Created a JavaScript file for dynamic language switching
3. Updated the main URLs file to include Django's i18n URL patterns
4. Added a CSRF token to the base.html template for the language switcher
5. Created the locale directory structure and a basic .po file for Bulgarian

## How to Complete the Setup

To complete the setup, you need to install GNU gettext tools and compile the translation files:

### For Windows:

1. Download and install GNU gettext tools from https://mlocati.github.io/articles/gettext-iconv-windows.html
2. Add the bin directory of the installed gettext tools to your PATH
3. Restart your command prompt or PowerShell
4. Run the following commands to generate and compile translation files:

```
python manage.py makemessages -l bg
python manage.py compilemessages
```

### For Linux/Mac:

1. Install gettext using your package manager:
   - For Ubuntu/Debian: `sudo apt-get install gettext`
   - For Mac (with Homebrew): `brew install gettext`
2. Run the following commands to generate and compile translation files:

```
python manage.py makemessages -l bg
python manage.py compilemessages
```

## How It Works

1. The language switcher is added to the navbar in base.html
2. When a user clicks on a flag, the JavaScript code submits a form to Django's set_language view
3. Django changes the language and redirects the user back to the current page
4. The page is displayed in the selected language

## Files Modified

- templates/base.html: Added language switcher to the navbar
- pet_mvp/urls.py: Added i18n URL patterns
- staticfiles/scripts/language-switcher.js: Created for dynamic language switching
- locale/bg/LC_MESSAGES/django.po: Created for Bulgarian translations