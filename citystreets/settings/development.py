from citystreets.settings.common import *  # noqa: F403 F401

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "&fnx8u(w_wkn$by1)@z233)w)vg5u(@bmt=aaom^i6(dxvt_!4"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []

# ALLAUTH

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
