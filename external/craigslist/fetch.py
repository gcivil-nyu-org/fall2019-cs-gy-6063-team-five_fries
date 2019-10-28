from craigslist import CraigslistHousing
from typing import Dict, List


def fetch_craigslist_housing(*, limit, **kwargs) -> List[Dict[str, any]]:
    query = CraigslistHousing(**kwargs)
    return list(query.get_results(geotagged=True, limit=limit))
