from citystreets.settings.common import *  # noqa: F403 F401

DEBUG = False

SECRET_KEY = os.environ["DJANGO_SECRET_KEY"]  # noqa: F405

ALLOWED_HOSTS = ["develop-branch.herokuapp.com/", "master-branch.herokuapp.com/"]

# Email information
EMAIL_USE_TLS = True
EMAIL_HOST = "smtp.gmail.com"
EMAIL_HOST_USER = "team.five.fries@gmail.com"
EMAIL_HOST_PASSWORD = "90d#C0Yx4EHxh4!mN4er1Z7"
EMAIL_PORT = 587
