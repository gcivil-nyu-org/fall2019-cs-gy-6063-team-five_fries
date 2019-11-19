import attr


@attr.s
class Address(object):
    street = attr.ib()
    zipcode = attr.ib(converter=str)
    city = attr.ib()
    state = attr.ib()
    latitude = attr.ib(converter=float)
    longitude = attr.ib(converter=float)

    @classmethod
    def from_dict(cls, dic):
        return cls(**dic)

    @property
    def full_address(self):
        components = [self.street, self.city, self.state, self.zipcode]
        return ", ".join(filter(lambda x: x, components))
