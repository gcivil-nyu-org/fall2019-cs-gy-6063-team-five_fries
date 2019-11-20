import sys
import os

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from external.res import get_res_data  # noqa: E402

usage = """
usage:
    get_res_data.py 10009
"""


def main():
    if len(sys.argv) < 2:
        print(usage)
        return

    results = get_res_data(sys.argv[1])
    for r in results:
        print(r)


if __name__ == "__main__":
    main()
