from .base import ErConnector


class Communication(object):

    def __init__(self, communication_id, data=None):
        self.communication_id = communication_id
        if not data:
            # Fetch from remote
            self.refresh()
        else:
            # Allows it to be populated by list_communication_methods without an additional fetch
            self.data = data
            self.populate_from_data()

    def refresh(self):
        self.data = get_communication_by_id(self.communication_id).data
        self.populate_from_data()

    def populate_from_data(self):
        self.type_id = self.data['TypeID']
        self.category_id = self.data['CategoryID']
        self.value = self.data['Value']
        self.is_primary = self.data['IsPrimary']

    def save(self, payload):
        data = self.data
        for item in payload.keys():
            data[item] = payload[item]
        connector = ErConnector()
        url = 'Communication/{communication_id}/'.format(communication_id=self.communication_id)
        response = connector.send_request(
            path=url,
            verb='PUT',
            payload=data
        )
        try:
            self.data = response
            return [True, self]
        except Exception as e:
            return [False, 'An error occured updating the Communication Method. The error was: '.format(e=e)]

    def delete(self):
        return delete_communication_method(self.communication_id)

    def set_value(self, value):
        return self.save({'Value':value})

    def get_value(self):
        return self.data['Value']

    def set_is_primary(self, Value):
        #set a communication method to Primary.
        result = self.save({'IsPrimary':Value})
        self.refresh()
        return result

    def make_primary(self):
        result = self.set_is_primary(True)
        return result

class CommunicationCategory(object):

    def __init__(self, data):
        self.data = data
        self.id = self.data['ID']
        self.category_id = self.id
        self.name = self.data['Name']

    def __str__(self):
        return self.name

def get_communication_by_id(communication_id):
    # Get a communication with the provided Id
    connector = ErConnector()
    url = 'Communication/{communication_id}/'.format(communication_id=communication_id)
    response = connector.send_request(
        path=url
    )
    return Communication(communication_id=response['ID'], data=response)


def list_communication_methods(type, refid=None, about_id=None, is_primary=False):
    # Get all Communications for the an entity of the Type type, and with the Id refId
    # eg "Get all communication methods for Candidate ID 12345 -> list_communication_methods('Candidate', 12345)
    connector = ErConnector()  # 2.0 API
    if refid:
        url = 'Communication/ByAboutId/{Type}/{refId}'.format(
            Type=type,
            refId=refid
        )
    else:
        url = 'Communication/'.format(
            Type=type,
        )
    response = connector.send_request(
        path=url,
        verb='GET'
    )
    methods = [Communication(communication_id=method['ID'], data=method) for method in response]

    if about_id:
        methods = [method for method in methods if method.type_id == about_id]

    if is_primary:
        methods = [method for method in methods if method.is_primary is True]

    return methods

def list_communication_categories(name=None, id=None):
    connector = ErConnector()  # 2.0 API
    url = 'Communication/Category'

    response = connector.send_request(
        path=url,
        verb='GET'
    )

    categories = [CommunicationCategory(category) for category in response]
    if name:
        try:
            categories = [category for category in categories if category.name == name]
            return categories[0]
        except:
            return None
    elif id:
        try:
            categories = [category for category in categories if category.category_id == id]
            return categories[0]
        except:
            return None
    else:
        return categories

def get_communication_category_by_name(name):
    return list_communication_categories(name)

def get_communication_category_by_id(id):
    return list_communication_categories(id)

def delete_communication_method(communication_id):
    connector = ErConnector()
    url = 'Communication/{communication_id}/'.format(communication_id=communication_id)
    response = connector.send_request(
        path=url,
        verb='DELETE',
        rawresponse=True
    )
    if response.status_code == 204:

        return (True, "The Communication Method was deleted successfully")
    else:
        return (False, response.json()['Message'])

def add_communication_method(abouttype_id, type_id, obj_id, value, is_primary=False):
    connector = ErConnector()
    url = 'Communication/{abouttype_id}/{obj_id}/'.format(
        abouttype_id=abouttype_id,
    obj_id=obj_id)
    data = {}
    data['AboutType'] = abouttype_id
    data['Id'] = obj_id
    data['TypeID'] = type_id
    data['Value'] = value
    data['IsPrimary'] = is_primary
    response = connector.send_request(
        path=url,
        verb='POST',
        payload=data
    )

    return Communication(communication_id=response['ID'], data=response)
