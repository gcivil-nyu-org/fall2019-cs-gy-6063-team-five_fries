import sys
import os

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from external.googleapi import normalize_us_address  # noqa: E402

usage = """
usage:
    python normalize_us_address.py "6 Jay St"
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
