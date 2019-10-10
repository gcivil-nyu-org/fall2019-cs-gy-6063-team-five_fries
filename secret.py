import os

# should add the environmental varible ZWSID
# e.g. export ZWSID = "abcdefg"
def getZwsId():
    return os.environ['ZWSID']
