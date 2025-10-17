from .base import *


DEBUG = os.getenv("DJANGO_DEBUG", "False") == "True"

# ALLOWED_HOSTS can be comma-separated in env, e.g. "*" or "example.com,10.244.0.58"
ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "*").split(",")