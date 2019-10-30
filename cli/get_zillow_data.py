import sys
import os

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from external.zillow import get_zillow_housing  # noqa: E402


if __name__ == "__main__":
    data = get_zillow_housing(
        address="3rd Ave", city_state="Brooklyn, NY", show_rent_z_estimate=True
    )

    for result in data:
        print(result)
