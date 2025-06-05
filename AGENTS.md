# 🧠 Codex Agent Instructions: Environment Activation & Commands

This project requires specific setup steps to ensure all dependencies (like Django, Redis, Celery) are available and working in Codex or any containerized environment.

---
## General instruction
1. Create virtual environment
``` bash 
 python3 -m venv .venv
 ```


2. Use following command to activate the environment before running any tests:
The virtual environment `.venv` is created in the project root (/workspace). Always activate it before running commands:

```bash
source .venv/bin/activate
```

# Install requirements and prepare Django
pip install --upgrade pip
pip install -r requirements.txt

python manage.py migrate
python manage.py compilemessages
python load_fixtures.py
python caller.py

# Start Celery worker and beat
# (Consider using tmux or separate terminals if needed)
celery -A pet_mvp worker --loglevel=info &
celery -A pet_mvp beat --loglevel=info &

## Run tests