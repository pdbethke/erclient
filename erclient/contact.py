from .base import ErConnector, DataHelper
from .company import Company
from .config import rest_entity_id
from .owner import get_owners
from .adsource import get_adsource_for_obj
from .address import get_address_by_id
from .communication import list_communication_methods



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
        self.full_name = self.get_full_name()
        self.company_id = self.data.get('CompanyID', None)
        self.title = self.data.get('Title', None)
        self.status_id = self.data.get('StatusID', None)
        self.default_address_id = self.data.get('DefaultAddressID', None)
        self.role_id = self.data.get('RoleID', None)
        self.type_id = self.data.get('TypeID', None)

    def get_full_name(self, include_middle=False):
        if include_middle:
            return '{fname} {mname} {lname}'.format(
                fname=self.first_name,
                mname=self.middle_name,
                lname=self.last_name)
        else:
            return '{fname} {lname}'.format(
                fname=self.first_name,
                lname=self.last_name)

    def get_company(self):
        return Company(self.company_id)

    def get_address(self):
        return get_address_by_id(self.default_address_id)

    def get_owners(self):
        return get_owners('Contact', self.contact_id)

    def get_rest_data(self):
        return get_contact_rest_data(self.contact_id)

    def get_status(self):
        return get_contact_status_by_id(int(self.status_id))

    def get_status_name(self):
        return self.get_status()['Name']

    def get_adsource(self):
        return get_adsource_for_obj(obj_id=self.contact_id, abouttype_id='Contact')

    def get_adsource_name(self):
        return self.get_adsource().name

    def get_adsource_id(self):
        return self.get_adsource().adsource_id

    def list_communication_methods(self):
        return list_communication_methods('Contact', refid=self.contact_id)

    def get_primary_email_obj(self):
        return [x for x in self.list_communication_methods() if x.is_primary is True and x.type_id == 200][0]
    def get_secondary_email_objs(self):
        return [x for x in self.list_communication_methods() if x.is_primary is False and x.type_id == 200]
    def get_secondary_email_address(self):
        objs = self.get_secondary_email_objs()
        return objs[0] if objs else None

    def get_primary_email_address(self):
        return self.get_primary_email_obj().value
    def get_primary_phone_obj(self):
        try:
            return [x for x in self.list_communication_methods() if x.is_primary is True and x.type_id == 100][0]
        except:
            return [x for x in self.list_communication_methods() if x.type_id == 100][0]

    def get_primary_phone(self):
        val = self.get_primary_phone_obj()
        return val.value if val else None



    def export_to_bullhorn(self):

        # customzed mapping to Bullhorn import specifications

        out = {}
        out['firstName'] = self.first_name
        out['lastName'] = self.last_name
        recruiters = self.get_owners()
        default_address = get_address_by_id(self.default_address_id)
        if recruiters:
            out['recruiterUserID'] = recruiters[0].user_id
        else:
            out['recruiterUserID'] = None
        out['status'] = self.get_status_name()
        out['source'] = self.get_adsource_name()
        out['clientCorporationID'] = self.company_id
        out['reportToUserID'] = None
        out['occupation'] = self.title
        out['division'] = None
        out['customText10'] = None
        out['skillID'] = None
        out['customText5'] = None
        out['customText14'] = None
        out['customTextBlock2'] = None
        out['email'] = self.get_primary_email_address()
        out['email2'] = self.get_secondary_email_address()
        out['address1'] = default_address.address_line_1
        out['address2'] = default_address.address_line_2
        out['city'] = default_address.city
        out['state'] = default_address.state_name
        out['zip'] = default_address.postal_code
        out['phone'] = self.get_primary_phone()
        out['mobile'] = None
        out['phone2'] = None
        out['fax'] = None
        out['customText15'] = None
        out['preferredContact'] = None
        out['comments'] = None
        out['customText18'] = None
        out['customTextBlock5'] = None
        out['customTextBlock4'] = None
        out['referredByUserID'] = None
        out['customText4'] = None
        out['customText2'] = None
        out['customText12'] = None
        out['customText6'] = None
        out['customText7'] = None
        out['dateAdded'] = None
        out['massMailOptOut'] = None


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

    return response

def get_contact_status_by_id(contact_status_id):
    try:
        return [x for x in list_contact_statuses() if int(x['ID']) == contact_status_id][0]
    except:
        return None