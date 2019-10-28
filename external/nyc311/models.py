import attr


@attr.s
class NYC311Complaint(object):
    created_date = attr.ib()
    incident_zip = attr.ib()
    incident_address = attr.ib()
    city = attr.ib()
    complaint_type = attr.ib()
    descriptor = attr.ib()
    status = attr.ib()


@attr.s
class NYC311Statistics(object):
    complaint_type = attr.ib()
    complaint_level = attr.ib()
    total_complaints_query_zip = attr.ib()
    closed_complaints_query_zip = attr.ib()
    percentage_complaints_closed = attr.ib()
    max_complaints = attr.ib()
    max_complaints_zip = attr.ib()
