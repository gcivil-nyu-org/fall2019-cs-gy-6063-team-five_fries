import sys
import os

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from external.googleapi import fetch_reverse_geocode  # noqa: E402

if __name__ == "__main__":
    data = fetch_reverse_geocode((40.763374, -73.910995))

    for result in data:
        print(result)
