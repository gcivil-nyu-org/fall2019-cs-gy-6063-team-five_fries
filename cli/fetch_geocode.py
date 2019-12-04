import sys
import os
import django

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "citystreets.settings")
django.setup()

from external.googleapi import fetch_geocode  # noqa: E402

if __name__ == "__main__":
    data = fetch_geocode("11103")

    for result in data:
        print(result)
