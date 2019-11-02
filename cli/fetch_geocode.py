import sys
import os
from external.googleapi import fetch_geocode

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))


if __name__ == "__main__":
    data = fetch_geocode("11103")

    for result in data:
        print(result)
