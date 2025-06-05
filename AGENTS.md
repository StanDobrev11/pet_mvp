# 🧠 Codex Agent Instructions: Environment Activation & Commands

This project requires specific setup steps to ensure all dependencies (like Django, Redis, Celery) are available and working in Codex or any containerized environment.

---
## General instruction
1. Create virtual environment
``` bash 
 python3 -m venv .venv
 ```


2. Use following command to activate the environment before running any tests:
The virtual environment `.venv` is created in the project (/workspace/pet_mvp/.venv). Always activate it before running commands:

```bash
source .venv/bin/activate
```
If the venv is successfully activated, you can skip installing the requirements

# Install requirements and prepare Django
pip install --upgrade pip
pip install -r requirements.txt

# To run this commands, you must navigate to /workspace/met_mvp/ and have the venv activated
python manage.py migrate
python manage.py compilemessages
python load_fixtures.py
python caller.py


# Start Celery worker and beat if not already started during creation of the env
# (Consider using tmux or separate terminals if needed)
celery -A pet_mvp worker --loglevel=info &
celery -A pet_mvp beat --loglevel=info &

## Run tests
Navigate to /workspace/pet_mvp and run
```bash
python manage.py test
```