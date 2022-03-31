from .base import ErConnector, DataHelper
from .company import Company
from .config import rest_entity_id
from .owner import get_owners




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
        self.middle_name = self.data.get('Middle', None)
        self.company_id = self.data.get('CompanyID', None)
        self.title = self.data.get('Title', None)
        self.status_id = self.data.get('StatusID', None)
        self.default_address_id = self.data.get('DefaultAddressID', None)
        self.role_id = self.data.get('RoleID', None)
        self.type_id = self.data.get('TypeID', None)

    def get_company(self):
        return Company(self.company_id)

    def get_owners(self):
        return get_owners('Contact', self.contact_id)

    def get_rest_data(self):
        return get_contact_rest_data(self.contact_id)

    def export_to_bullhorn(self):
        out = {}
        out['firstName'] = self.first_name
        out['lastName'] = self.last_name
        recruiters = self.get_owners()
        if recruiters:
            out['recruiterUserID'] = recruiters[0].user_id
        else:
            out['recruiterUserID'] = None
        out['status'] = None

        return out

def get_contact_by_id(contact_id):
    connector = ErConnector()  # 2.0 API
    url = 'Contact/{contact_id}'.format(
        contact_id=contact_id,
    )
    response = connector.send_request(
        path=url,
        verb='GET',
    )

    return Contact(response['ID'], data=response)


def get_contact_rest_data(contact_id):
    # Use 1.0 api to grab contact xml OBJ to get certain values not implemented yet in 2.0 API
    connector = ErConnector(api_version='rest')
    path = 'Contact/{EntityID}/{ContactID}/'.format(
        EntityID=rest_entity_id,
        ContactID=contact_id,
    )
    response = connector.send_request(
        path=path,
        verb='GET',
        rawresponse=True
    )

    try:
        return response.text
    except Exception as e:
        print(e)
        return None

def list_contact_statuses():
    connector = ErConnector()  # 2.0 API
    url = 'Contact/Status'
    response = connector.send_request(
        path=url,
        verb='GET',
    )

    return Contact(response['ID'], data=response)