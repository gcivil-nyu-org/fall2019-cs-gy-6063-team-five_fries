from citystreets.settings.common import *  # noqa: F403 F401

DEBUG = False

SECRET_KEY = os.environ["DJANGO_SECRET_KEY"]  # noqa: F405

ALLOWED_HOSTS = ["develop-branch.herokuapp.com/", "master-branch.herokuapp.com/"]

# Email information
EMAIL_USE_TLS = True
EMAIL_HOST = "smtp.gmail.com"
EMAIL_HOST_USER = os.environ["EMAIL_HOST_USER"]
EMAIL_HOST_PASSWORD = os.environ["EMAIL_HOST_PASSWORD"]
EMAIL_PORT = 587
