import os


def get_craigslist_response(name) -> str:
    filepath = os.path.join(os.path.dirname(__file__), "sample-response", name)
    with open(filepath) as f:
        return f.read()
