from .base import ErConnector

class Address(object):

    def __init__(self, address_id, data=None):
        self.address_id = address_id
        self.data = None
        if not data:
            # Fetch from remote
            self.refresh()
        else:
            # Allows it to be populated by list_communication_methods without an additional fetch
            self.data = data
            self.populate_from_data()

    def refresh(self):
        self.data = get_address_by_id(self.address_id).data
        self.populate_from_data()

    def populate_from_data(self):
        self.address_line_1 = self.data.get('AddressLine1', None)
        self.address_line_2 = self.data.get('AddressLine2', None)
        self.city = self.data.get('City', None)
        # Not really a neccesary lookup given that the state obj is so thin!
        # self.state = AddressState(address_state_id=self.data.get('StateID', None))
        self.state_id = self.data.get('StateID', None)
        self.state_name = self.data.get('State', None)
        self.state_code = self.data.get('StateCode', None)
        # Not really a neccesary lookup given that the region obj is so thin!
        # if self.data.get('RegionID', None):
        #     self.region = AddressRegion(address_region_id=self.data.get('RegionID'))
        # else:
        #     self.region = None
        self.postal_code = self.data.get('PostalCode', None)
        self.country_id = self.data.get('CountryID', None)
        self.country_code = self.data.get('CountryCode', None)

    def get_state(self):
        return AddressState(address_state_id=self.data.get('StateID', None))
    def get_region(self):
        return AddressRegion(address_region_id=self.data.get('RegionID'))

    def delete(self):
        return delete_address(self.address_id)

    def make_default(self):
        connector = ErConnector()
        url = 'Address/{id}/'.format(id=self.address_id)

    def save(self, payload):
        data = self.data
        for item in payload.keys():
            data[item] = payload[item]
        connector = ErConnector()
        url = 'Address/{id}/'.format(id=self.address_id)
        response = connector.send_request(
            path=url,
            verb='PUT',
            payload=data
        )
        try:
            self.data = response
            return self
        except Exception as e:
            raise Exception('An error occured updating the Address. The error was: '.format(e=e))

class AddressType(object):

    def __init__(self, address_type_id, data=None):
        self.address_type_id = address_type_id
        self.data = None
        if not data:
            # Fetch from remote
            self.refresh()
        else:
            # Allows it to be populated by list_communication_methods without an additional fetch
            self.data = data
            self.populate_from_data()

    def refresh(self):
        self.data = get_address_type_by_id(self.address_type_id).data
        self.populate_from_data()

    def populate_from_data(self):
        self.name = self.data.get('Name', None)

class AddressState(object):

    def __init__(self, address_state_id, data=None):
        self.address_state_id = address_state_id
        self.data = None
        if not data:
            # Fetch from remote
            self.refresh()
        else:
            # Allows it to be populated by list_communication_methods without an additional fetch
            self.data = data
            self.populate_from_data()

    def refresh(self):
        self.data = get_address_state_by_id(self.address_state_id).data
        self.populate_from_data()

    def populate_from_data(self):
        self.name = self.data.get('Name', None)
        self.state_code = self.data.get('StateCode', None)

class AddressRegion(object):

    def __init__(self, address_region_id, data=None):
        self.address_region_id = address_region_id
        self.data = None
        if not data:
            # Fetch from remote
            self.refresh()
        else:
            # Allows it to be populated by list_communication_methods without an additional fetch
            self.data = data
            self.populate_from_data()

    def refresh(self):
        self.data = get_address_region_by_id(self.address_region_id).data
        self.populate_from_data()

    def populate_from_data(self):
        self.name = self.data.get('Name', None)

def list_addresses(type, id):
    connector = ErConnector()  # 2.0 API
    url = 'Address/{AboutType}/{id}'.format(
        AboutType=type,
        id=id
    )
    response = connector.send_request(
        path=url,
    )

    return [Address(address_id=address['AddressID'], data=address) for address in response]

def get_default_address(type, id):
    connector = ErConnector()  # 2.0 API
    url = 'Address/{AboutType}/{id}/Default'.format(
        AboutType=type,
        id=id
    )
    response = connector.send_request(
        path=url,
    )

    try:
        return Address(address_id=response['AddressID'], data=response)
    except:
        return None


def add_address(
        abouttype_id,
        type_id,
        obj_id,
        address_line_1,
        city,
        state_id=None,
        region_id=None,
        postal_code=None,
        address_line_2=None,
        country_id=220,
        default=False
):
    connector = ErConnector()  # 2.0 API
    url = 'Address/{AboutType}/{Id}'.format(
        AboutType=abouttype_id,
        Id=obj_id,

    )

    data = {
            'AddressLine1': address_line_1,
            'AddressLine2': address_line_2,
            'City': city,
            'PostalCode': postal_code,
            'StateID': state_id,
            'CountryID': country_id,
            'RegionID': region_id,
            'TypeID': type_id,
            'makeDefault':True}

    response = connector.send_request(
        path=url,
        verb='POST',
        payload=data
    )
    if default:
        set_default_address(abouttype_id, obj_id, response['AddressID'])

    return Address(response['AddressID'], data=response)

def set_default_address(type, obj_id, address_id):
    connector = ErConnector()
    url = 'Address/{AboutType}/{Id}/Default/{address_id}'.format(
        AboutType=type,
        Id=obj_id,
        address_id=address_id)

    response = connector.send_request(
        path=url,
        verb='PATCH'
    )
    return response


def get_address_by_id(id, pathonly=False):
    connector = ErConnector()  # 2.0 API
    url = 'Address/{Id}/'.format(
        Id=id
    )
    response = connector.send_request(
        path=url,
    )

    return Address(response['AddressID'], data=response)


def delete_address(id):
    connector = ErConnector()  # 2.0 API
    url = 'Address/{id}/'.format(
        id=id
    )
    response = connector.send_request(
        path=url,
        verb='DELETE',
        rawresponse=True
    )

    if response.status_code == 204:

        return (True, "The Address was deleted successfully")
    else:
        return response.content

def list_address_regions():
    connector = ErConnector()  # 2.0 API
    url = 'Address/Region/'
    response = connector.send_request(
        path=url,
    )

    return  [AddressRegion(address_region_id=x['ID'], data=x) for x in response]

def get_address_region_by_id(address_region_id):
    try:
        return [x for x in list_address_regions() if x.address_region_id == address_region_id]
    except:
        return None

def get_address_region_id_by_name(name):
    try:
        return [x.address_region_id for x in list_address_regions() if x.name == name][0]
    except:
        return None

def list_address_states():
    connector = ErConnector()  # 2.0 API
    url = 'Address/State/'
    response = connector.send_request(
        path=url,
    )

    return  [AddressState(address_state_id=x['ID'], data=x) for x in response]

def get_address_state_by_id(address_state_id):
    try:
        return [x for x in list_address_states() if x.address_state_id == address_state_id][0]
    except:
        return None

def get_address_state_id_by_name(name, states=None):
    # allow to be populated with an external call to eliminate multiple lookups
    if not states:
        states = list_address_states()
    return [x.address_state_id for x in states if x.name == name][0]

def list_address_countries():
    connector = ErConnector()  # 2.0 API
    url = 'Address/Country/'
    response = connector.send_request(
        path=url,
    )

    return response

def get_address_country_id_by_name(name):
    try:
        return [x for x in list_address_countries() if x['Name'] == name][0]['ID']
    except:
        return None

def list_address_types():
    connector = ErConnector()  # 2.0 API
    url = 'Address/Type/'
    response = connector.send_request(
        path=url,
    )

    return [AddressType(address_type_id=x['ID'], data=x) for x in response]

def get_address_type_id_by_name(name):
    try:
        return [x.address_type_id for x in list_address_types() if x.name == name][0]
    except:
        return None

def get_address_type_by_id(address_type_id):
    try:
        return [x for x in list_address_types() if x.address_type_id == address_type_id]
    except:
        return None