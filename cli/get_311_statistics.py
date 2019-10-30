import sys
import os

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from external.nyc311 import get_311_statistics  # noqa: E402

if __name__ == "__main__":
    try:
        complaint_results = get_311_statistics(10009)  # valid zip code
    except TimeoutError:
        print("Timeout")

    print("RESULTS FOR VALID ZIP CODE:")
    print("No matches =", len(complaint_results) == 0)
    for result in complaint_results:
        print(result)
        print("------------------")
    print("------------------")

    try:
        complaint_results = get_311_statistics(100099)  # valid zip code
    except TimeoutError:
        print("Timeout")

    print("RESULTS FOR INVALID ZIP CODE:")
    print("No matches =", len(complaint_results) == 0)
    for result in complaint_results:
        print(result)
        print("------------------")
    print("------------------")
