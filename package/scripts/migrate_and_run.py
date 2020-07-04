#!/usr/bin/env python
import os
import sys
from django.core.management import call_command


def main():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError("Couldn't import Django.") from exc
    
    print("Initializing the database...\n")
    execute_from_command_line(["manage.py", "makemigrations"])
    execute_from_command_line(["manage.py", "makemigrations", "backend"])
    execute_from_command_line(["manage.py", "migrate"])
    print("Starting server...\n")
    execute_from_command_line(["manage.py", "runserver"])

