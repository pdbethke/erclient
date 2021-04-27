from dateutil.parser import parse

from .base import ErConnector

class Timesheet(object):

    def __init__(self, timesheet_id, data):
        self.timesheet_id = timesheet_id
        self.data = data
        self.populate_from_data()

    def refresh(self):
        self.populate_from_data()

    def populate_from_data(self):
        self.start_date = parse(self.data.get('StartDate', None))
        try:
            self.end_date = parse(self.data.get('EndDate', None))
        except:
            self.end_date = None
        try:
            self.pay_period_date = parse(self.data.get('PayPeriodEndDate', None))
        except:
            self.pay_period_date = None
        try:
            self.submitted_date = parse(self.data.get('SubmittedDate', None))
        except:
            self.submitted_date = None
        try:
            self.approved_date = parse(self.data.get('ApprovedDate', None))
        except:
            self.approved_date = None

def list_candidate_timesheets(candidate_id):
    connector = ErConnector()  # 2.0 API
    url = 'Timesheet/Candidate/{candidate_id}'.format(
        candidate_id=candidate_id,
    )
    response = connector.send_request(
        path=url,
        verb='GET',
    )
    return [Timesheet(timesheet_id=data['ID'], data=data) for data in response]

