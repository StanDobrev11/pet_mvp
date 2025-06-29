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

```sh
python manage.py makemessages -l bg -i venv -i .venv -i node_modules -i staticfiles -i media
```

This will create or update the `.po` file for Bulgarian at:
```
locale/bg/LC_MESSAGES/django.po
```

For JavaScript files, use:

```sh
python manage.py makemessages -d djangojs -l bg -i venv -i .venv -i node_modules -i staticfiles -i media
```

This will create or update:
```
locale/bg/LC_MESSAGES/djangojs.po
```

#### 2. Translating Messages

Edit the `.po` files in the `locale/bg/LC_MESSAGES/` directory to add translations for each message. Each message has an `msgid` (the original string) and an `msgstr` (the translated string).

Example:
```
msgid "Welcome"
msgstr "Добре дошли"
```

To help manage untranslated and fuzzy strings, you can extract only untranslated and fuzzy entries from your `.po` file using:

```sh
msgattrib --untranslated -o untranslated.po django.po        
msgattrib --fuzzy -o untranslated.po django.po
```

You can then merge translations back using:

```sh
msgcat django.po untranslated.po --use-first -o django.po
```

#### 3. Compiling Messages

After translating the messages, compile them into `.mo` files:

```sh
python manage.py compilemessages -l bg
```

This creates binary `.mo` files that Django uses for translations at runtime, in the same `locale/bg/LC_MESSAGES/` directory.

#### 4. Adding New Languages

To add support for a new language:

1. Add the language to the `LANGUAGES` list in `settings.py`
2. Run `python manage.py makemessages -l <lang_code>` to create the `.po` file (e.g., `python manage.py makemessages -l de`)
3. Translate the messages in the `.po` file at `locale/<lang_code>/LC_MESSAGES/django.po`
4. Compile the messages with `python manage.py compilemessages -l <lang_code>`

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

## Clinic Model and Access Workflow

The application defines two proxy models over the main `AppUser` model: `Owner`
and `Clinic`. Clinics use the same authentication fields as owners but store
clinic-specific information such as the clinic name and address. These fields
are defined in `pet_mvp/accounts/models.py` and a boolean `is_approved` keeps
track of administrator approval:

```python
class Clinic(AppUser):
    class Meta:
        proxy = True
        verbose_name = _("Clinic")
        verbose_name_plural = _("Clinics")
```

Clinics register through the **Access Code** workflow. When a clinic submits an
access code and email address, the application checks if that email already
exists. New clinics are redirected to a registration form where their account is
created inactive and a request for approval is sent to the pet owners:

```python
def form_valid(self, form):
    clinic = form.instance
    clinic.is_active = False
    ...
    send_clinic_owner_access_request_email(...)
    send_clinic_admin_approval_request_email(...)
```

Owners approve access via a link that activates the clinic account:

```python
if not clinic.is_active:
    clinic.is_active = True
    clinic.save()
```

Once approved and active, clinics enter their password to access the pet’s
records. The **Clinic Dashboard** lists all pets the clinic has temporary access
to via the `VetPetAccess` model.

Clinics are therefore intended for veterinary practices that manage medical
records on behalf of pet owners. They can view and add examinations only while a
valid access grant is active.

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

## Running Tests

To run the project's test suite, use Django's built-in ``test`` command. The
``manage.py`` script automatically switches to the test settings when invoked
with this command, so no additional environment configuration is needed:

```bash
python manage.py test
```

The tests use an in-memory SQLite database defined in ``tests/settings.py``.

## Using Docker Compose

You can also run the project using Docker Compose. This will start the Django
application along with Redis, Celery workers, Celery Beat, Mailhog and Nginx:

```bash
docker-compose up --build
```

The site will be available at ``http://localhost:8000`` and Mailhog can be
accessed at ``http://localhost:8025``. Stop the containers with
``docker-compose down`` when you are finished.

## Configuring the Site domain

If your generated ``sitemap.xml`` contains ``example.com`` URLs, update the
default ``Site`` entry in the Django admin. Navigate to ``/admin/sites/site/1``
and set the ``domain`` and ``name`` fields to match your real deployment
domain. This ensures the sitemap links use the correct hostname and avoids
errors like "This url is not allowed for a Sitemap at this location" during
sitemap validation.

## Sitemap and robots.txt

The project provides SEO resources for search engines. A dynamic sitemap is available at `/sitemap.xml` and is generated using Django's sitemap framework. The `StaticViewSitemap` in `pet_mvp/common/sitemaps.py` lists important public URLs, and the URL pattern for the sitemap is defined in `pet_mvp/urls.py`.

A plain-text `robots.txt` is served at `/robots.txt` through the `robots_txt` view in `pet_mvp/common/views.py`. It allows all pages to be indexed and points crawlers to the sitemap:

```
User-Agent: *
Disallow:
Sitemap: https://<your-domain>/sitemap.xml
```

Ensure the domain configured in the Django `Site` model matches your deployment so the generated URLs in these files are correct.

## GitHub Actions

This project uses GitHub Actions for continuous integration and deployment. The workflow automates testing, linting, and deployment processes.

### Workflow Configuration

The main workflow is defined in `.github/workflows/ci.yml` and includes:

1. Running Tests:
   ```yaml
   - name: Run Tests
     run: |
       python manage.py test
   ```

2. Linting with flake8:
   ```yaml
   - name: Run Linting
     run: |
       flake8 .
   ```

3. Checking for migrations:
   ```yaml
   - name: Check Migrations
     run: |
       python manage.py makemigrations --check --dry-run
   ```

4. Deployment to production (on main branch):
   ```yaml
   - name: Deploy to Production
     if: github.ref == 'refs/heads/main'
     run: |
       ./deploy.sh
   ```

### Automated Tasks

The following tasks are automated through GitHub Actions:

- Running unit tests on every push and pull request
- Code quality checks with flake8
- Automated deployment to production when merging to main branch
- Daily vaccination report generation (via cronjob)
- Database backups (weekly)

## Deployment

### Prerequisites

1. Set up the following secrets in your GitHub repository:
   - `SSH_PRIVATE_KEY`: SSH key for server access
   - `SERVER_HOST`: Production server hostname
   - `SERVER_USER`: SSH user for deployment
   - `DJANGO_SECRET_KEY`: Django secret key
   - `DATABASE_URL`: Production database URL
   - `BREVO_API_KEY`: Brevo API key for email service

### Deployment Process

1. The `deploy.sh` script handles the deployment:
   ```bash
   #!/bin/bash
   ssh $SERVER_USER@$SERVER_HOST << 'ENDSSH'
   cd /path/to/pet_mvp
   git pull origin main
   source venv/bin/activate
   pip install -r requirements.txt
   python manage.py migrate
   python manage.py collectstatic --noinput
   sudo systemctl restart gunicorn
   sudo systemctl restart nginx
   ENDSSH
   ```

2. The script:
   - Pulls the latest code from the main branch
   - Updates dependencies
   - Applies database migrations
   - Collects static files
   - Restarts the application server (Gunicorn) and web server (Nginx)

### Cronjob Configuration

The following cronjobs are set up on the production server:

1. Daily Vaccination Report (runs at 6 AM UTC):
   ```crontab
   0 6 * * * cd /path/to/pet_mvp && source venv/bin/activate && python manage.py generate_vaccination_report
   ```

2. Weekly Database Backup (runs every Sunday at midnight):
   ```crontab
   0 0 * * 0 cd /path/to/pet_mvp && source venv/bin/activate && python manage.py dbbackup
   ```

### Monitoring

The application is monitored using:
- Server metrics via Prometheus
- Application logs through Django logging
- Email notifications for critical errors
- Daily health checks for all crucial services

### Rolling Back Changes

In case of deployment issues:

1. Access the server and switch to the last known good commit:
   ```bash
   git reset --hard <commit-hash>
   ```

2. Restore database from backup if needed:
   ```bash
   python manage.py dbrestore
   ```

3. Restart services:
   ```bash
   sudo systemctl restart gunicorn
   sudo systemctl restart nginx
   ```