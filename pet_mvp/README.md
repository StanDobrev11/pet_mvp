# Pet MVP Project

## Email Service Setup with Brevo and Celery

### Brevo Email Service

This project uses Brevo (formerly Sendinblue) for sending transactional emails. To set up:

1. Create a Brevo account at [https://www.brevo.com/](https://www.brevo.com/)
2. Generate an API key in the Brevo dashboard
3. Add your API key to the Django settings:


# Terminal 2: Start Celery worker
celery -A pet_mvp worker --loglevel=info --pool=solo  -> in windows
celery -A pet_mvp worker --loglevel=info

# Terminal 3: Start Celery Beat
celery -A pet_mvp beat --loglevel=info