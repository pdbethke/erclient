from .base import ErConnector

class Recruiter(object):

    def __init__(self, recruiter_id, data=None, is_primary=False, department_id=None):
        self.recruiter_id = recruiter_id
        self.is_primary=is_primary
        self.department_id = department_id
        if not data:
            # Fetch from remote
            self.refresh()
        else:
            # Allows it to be populated by list_communication_methods without an additional fetch
            self.data = data
            # self.refresh(fetch=False)
        self.populate_from_data()

    def refresh(self):
        self.data = get_recruiter_by_id(self.recruiter_id)
        self.populate_from_data()

    def populate_from_data(self):
        self.first_name = self.data.get('First', None)
        self.last_name = self.data.get('Last', None)
        self.full_name = '{first} {last}'.format(
            first = self.first_name,
            last = self.last_name
        )
        self.user_id = self.data['UserID']
        self.email_address = self.data['EmailAddress']
        self.title = self.data['Title']


def get_recruiter_by_id(id, is_primary=False):
    connector = ErConnector()  # 2.0 API
    url = 'Recruiter/{id}'.format(
        id=id,
    )
    response = connector.send_request(
        path=url,
        verb='GET',
    )

    return Recruiter(response['ID'], data=response, is_primary=is_primary, department_id=None)

def get_recruiter_by_email(email, is_primary=False):
    connector = ErConnector()  # 2.0 API
    url = 'Recruiter/ByEmail?Email={email}'.format(email=email)
    response = connector.send_request(
        url,
        verb='GET',
    )
    return Recruiter(response['ID'], data=response, is_primary=is_primary, department_id=None)