# boot_django.py
#
# This file sets up and configures Django. It's used by scripts that need to
# execute as if running in a Django server.
import os
import django
from django.conf import settings

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "backend"))
THEME_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "theme"))

def boot_django():
    settings.configure(
        BASE_DIR=BASE_DIR,
        ROOT_URLCONF="backend.urls",
        # TEMPLATE_DIR = os.path.join(BASE_DIR, 'templates'),
        TEMPLATES=[{
            'BACKEND': 'django.template.backends.django.DjangoTemplates',
            # if you want to render using template file
            'DIRS': [os.path.join(BASE_DIR, "templates"), os.path.join(THEME_DIR, "templates")]
        }],
        DEBUG=True,
        DATABASES={
            "default":{
                "ENGINE":"django.db.backends.sqlite3",
                "NAME": os.path.join(BASE_DIR, "db.sqlite3"),
            }
        },
        INSTALLED_APPS=(
            "backend", "theme", "tailwind", 'django.contrib.staticfiles',
        ),
        TAILWIND_APP_NAME = 'theme',
        STATIC_URL= "/static/",
        TIME_ZONE="UTC",
        USE_TZ=True,
    )
    django.setup()
