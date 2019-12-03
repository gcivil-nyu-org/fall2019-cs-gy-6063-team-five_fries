import sys
import os
import django

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "citystreets.settings")
django.setup()

from external.googleapi import normalize_us_address  # noqa: E402

usage = """
What it does:
    Normalize an address to the standard form. It handles upper/lowercase letter and a partial address, etc.

usage:
    python normalize_us_address.py "6 metrotech"

output:
    6 MetroTech Center, Brooklyn, NY, 11201
"""


def main():
    if len(sys.argv) < 2:
        print(usage)
        return

    addr = sys.argv[1]
    data = normalize_us_address(addr)
    print(data)
    print(data.full_address)


if __name__ == "__main__":
    main()
