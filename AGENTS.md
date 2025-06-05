# 🧠 Codex Agent Instructions: Environment Activation & Commands

This project requires specific setup steps to ensure all dependencies (like Django, Redis, Celery) are available and working in Codex or any containerized environment.

---
## General instruction

1. Use following command to activate the environment before running any tests:
The virtual environment `.venv` is created in the project root (/workspace). Always activate it before running commands:

```bash
cd /workspace
source .venv/bin/activate
cd pet_mvp
python manage.py test
```
If this does not work, try to activate venv in /workspace/pet_mvp
```bash
cd workspace/pet_mvp
source .venv/bin/activate
python manage.py test
```