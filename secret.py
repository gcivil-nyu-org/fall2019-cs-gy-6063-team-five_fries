import os


# should add the environmental varible ZWSID
# e.g. export ZWSID = "abcdefg"
def get_zws_id():
    return os.environ["ZWSID"]


def get_311_socrata_key():
    return os.environ["KEY_311"]
