from .base import ErConnector, DataHelper
from .company import Company



class Contact(DataHelper):

    def __init__(self, contact_id, data=None):
        self.contact_id = contact_id
        if not data:
            # Fetch from remote
            self.refresh()
        else:
            # Allows it to be populated by list_communication_methods without an additional fetch
            self.data = data
            # self.refresh(fetch=False)
        self.populate_from_data()
    def refresh(self):
        self.data = get_contact_by_id(self.contact_id).data
        self.populate_from_data()
    def populate_from_data(self):
        self.first_name = self.data.get('First', None)
        self.last_name = self.data.get('Last', None)
        self.company_id = self.data.get('CompanyID', None)
        self.title = self.data.get('Title', None)
        self.company_name = self.company().name

    def company_id(self):
        return self.get_field('CompanyID')

    def company(self):
        return Company(self.get_field('CompanyID'))


def get_contact_by_id(id):
    connector = ErConnector()  # 2.0 API
    url = 'Contact/{id}'.format(
        id=id,
    )
    response = connector.send_request(
        path=url,
        verb='GET',
    )

    return Contact(response['ID'], data=response)