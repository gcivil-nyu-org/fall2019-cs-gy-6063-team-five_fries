import sys
import os

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from external.googleapi import fetch_geocode

if __name__ == "__main__":
    data = fetch_geocode("11103")

    for result in data:
        print(result)
