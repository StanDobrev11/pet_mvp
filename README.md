# Pet MVP Project

## Project Overview

Pet MVP is a Django-based web application designed to help pet owners and veterinarians manage pet medical records. The application allows users to:

- Store and track pet information including vaccinations, treatments, and medical examinations
- Generate digital pet passports
- Receive notifications for upcoming vaccinations or treatments
- Share access to pet records with veterinarians through temporary access codes
- Support multiple languages (currently English and Bulgarian)

## Getting Started

### Prerequisites

- Python 3.8+
- Django 5.2+
- Redis (for Celery task queue)

### Installation

1. Clone the repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Run migrations:
   ```
   python manage.py migrate
   ```
4. Create a superuser:
   ```
   python manage.py createsuperuser
   ```
5. Run the development server:
   ```
   python manage.py runserver
   ```

## Internationalization and Localization

This project supports multiple languages using Django's internationalization framework. Currently, English and Bulgarian are supported.

### Generating and Compiling Translation Files

#### 1. Extracting Messages

To extract messages from your code and templates for translation, run:

```
python manage.py makemessages -l bg
```

This will create or update the `.po` file for Bulgarian in the `locale/bg/LC_MESSAGES/` directory.

For JavaScript files, use:

```
python manage.py makemessages -d djangojs -l bg
```

#### 2. Translating Messages

Edit the `.po` files in the `locale/bg/LC_MESSAGES/` directory to add translations for each message. Each message has an `msgid` (the original string) and an `msgstr` (the translated string).

Example:
```
msgid "Welcome"
msgstr "Добре дошли"
```

#### 3. Compiling Messages

After translating the messages, compile them into `.mo` files:

```
python manage.py compilemessages
```

This creates binary `.mo` files that Django uses for translations at runtime.

#### 4. Adding New Languages

To add support for a new language:

1. Add the language to the `LANGUAGES` list in `settings.py`
2. Run `python manage.py makemessages -l bg` to create the `.po` file
3. Translate the messages in the `.po` file
4. Compile the messages with `python manage.py compilemessages`

## Email Service Setup with Brevo and Celery

### Brevo Email Service

This project uses Brevo (formerly Sendinblue) for sending transactional emails. To set up:

1. Create a Brevo account at [https://www.brevo.com/](https://www.brevo.com/)
2. Generate an API key in the Brevo dashboard
3. Add your API key to the Django settings or environment variables

### Celery Setup

Celery is used for handling asynchronous tasks like sending emails and notifications. To run Celery:

#### Terminal 1: Start the Django server
```
python manage.py runserver
```

#### Terminal 2: Start Celery worker
```
# For Windows
celery -A pet_mvp worker --loglevel=info --pool=solo

# For Linux/Mac
celery -A pet_mvp worker --loglevel=info
```

#### Terminal 3: Start Celery Beat (for scheduled tasks)
```
celery -A pet_mvp beat --loglevel=info
```

## Using JSON Fixtures

You can use Django's fixture system to load and export data in JSON format.

### Loading Data

To load data from a fixture (e.g., `clinics.json`), run:

```sh
python manage.py loaddata accounts/fixtures/clinics.json
```

This will import the data into your database.

### Exporting Data

To export data from a model (e.g., `Clinic`), run:

```sh
python manage.py dumpdata accounts.Clinic --indent 2 > clinics.json
```

This will create a nicely formatted `clinics.json` file with all Clinic objects.

---

## Creating a Superuser with a Hashed Password in a Migration

If you want to create a superuser in an empty migration and need to set a hashed password, you can generate the hash using Django's shell:

```sh
python manage.py shell
```

Then, in the shell:

```python
from django.contrib.auth.hashers import make_password
print(make_password('1234'))  
```

Copy the resulting hash and use it in your migration when creating the superuser.

Example migration code:

```python
from django.db import migrations

def create_superuser(apps, schema_editor):
    User = apps.get_model('accounts', 'User')
    User.objects.create_superuser(
        email='admin@example.com',
        password='HASHED_PASSWORD_HERE', 
    )

class Migration(migrations.Migration):

    dependencies = [
        # ...your dependencies...
    ]

    operations = [
        migrations.RunPython(create_superuser),
    ]
```

Replace `'HASHED_PASSWORD_HERE'` with the hash you generated.

## Project Structure

- `pet_mvp/` - Main Django project directory
  - `accounts/` - User authentication and profile management
  - `pets/` - Pet information management
  - `records/` - Medical records and treatments
  - `drugs/` - Medications and vaccines
  - `notifications/` - Email notifications
  - `access_codes/` - Temporary access code generation
  - `common/` - Shared functionality
- `templates/` - HTML templates
- `staticfiles/` - CSS, JavaScript, and other static files
- `locale/` - Translation files
- `media/` - User-uploaded files

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
