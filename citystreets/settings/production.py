from citystreets.settings.common import *  # noqa: F403 F401

DEBUG = False

SECRET_KEY = os.environ["DJANGO_SECRET_KEY"]  # noqa: F405

ALLOWED_HOSTS = ["develop-branch.herokuapp.com/", "master-branch.herokuapp.com/"]
