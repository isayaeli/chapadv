#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    """Run administrative tasks."""
    # DJANGO_ENV = os.getenv('DJANGO_ENV', default='dev')
    # os.environ.setdefault('DJANGO_SETTINGS_MODULE', f'config.settings.{DJANGO_ENV}')

    DJANGO_ENV = os.getenv('DJANGO_ENV', 'development')
    
    # Validate environment
    valid_environments = ['development', 'staging', 'production']
    if DJANGO_ENV not in valid_environments:
        print(f"Warning: Invalid DJANGO_ENV '{DJANGO_ENV}'. Using 'development'.")
        DJANGO_ENV = 'development'
    
    # Set settings module
    settings_module = f'config.settings.{DJANGO_ENV}'
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', settings_module)
    
    print(f"Using settings: {settings_module}")  # Optional: for debugging

    try:
        from django.core.management import execute_from_command_line # pyright: ignore[reportMissingModuleSource]
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
