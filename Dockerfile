FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=pet_mvp.settings

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    gcc \
    gettext \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# set the workdir
WORKDIR /app

# update pip
RUN python -m pip install --upgrade pip

# Install Python dependencies
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . /app/

# Compile translations
RUN #python manage.py compilemessages

# Collect static files
RUN #python manage.py collectstatic --noinput

# Run gunicorn
#CMD ["gunicorn", "pet_mvp.wsgi:application", "--bind", "0.0.0.0:8000"]