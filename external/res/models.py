import attr


@attr.s
class ResComplaint(object):
    dba = attr.ib()
    boro = attr.ib()
    zipcode = attr.ib()
    violation_description = attr.ib()
