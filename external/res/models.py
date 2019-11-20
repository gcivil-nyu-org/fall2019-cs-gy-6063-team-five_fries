import attr


@attr.s
class ResComplaint(object):
    dba = attr.ib()
    boro = attr.ib()
    zipcode = attr.ib()
    violation_description = attr.ib()

    @classmethod
    def from_dict(cls, dic):
        return cls(
            dba=dic.get("dba"),
            boro=dic.get("boro"),
            zipcode=dic.get("zipcode"),
            violation_description=dic.get("violation_description"),
        )
