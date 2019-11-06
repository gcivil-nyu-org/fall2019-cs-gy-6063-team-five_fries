import sys
import os

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from external.nyc311 import get_311_data  # noqa: E402

if __name__ == "__main__":
    try:
        zipcode = 10000
        print("get_311_data() with valid zipcode", zipcode)
        query_results = get_311_data(zipcode, 5)  # valid zip code
        print(query_results)
        print("No match?", len(query_results) == 0)
    except TimeoutError:
        print("timeout")

    print("")

    try:
        zipcode = 1000099
        print("get_311_data() with invalid zipcode", zipcode)
        query_results = get_311_data(zipcode, 5)
        print("No match?", len(query_results) == 0)
        print(query_results)
    except TimeoutError:
        print("timeout")
