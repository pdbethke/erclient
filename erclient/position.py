from functools import lru_cache
from dateutil.parser import parse

from .base import ErConnector
from .contact import Contact, Company
from .department import get_department_by_id, Department
from .foldergroup import FolderGroup


class Position(object):

    def __init__(self, position_id, data=None, types=None):
        self.position_id = position_id
        self.types = types
        if not data:
            # Fetch from remote
            self.refresh()
        else:
            # Allows it to be populated by list methods without an additional fetch
            self.data = data
        self.populate_from_data()

    def refresh(self):
        self.data = get_position_by_id(self.position_id).data
        self.populate_from_data()

    def populate_from_data(self):
        self.title = self.data.get('Title', None)
        self.web_position_title = self.data.get('WebPositionTitle', None)
        self.web_description = self.data.get('WebDescription', None)
        self.contact_id = self.data.get('ContactID', None)
        self.primary_owner_id = self.data.get('PrimaryOwnerID', None)
        self.department = self.get_department()
        self.type = self.get_type()
        self.department_id = None
        self.type_id = None
        if self.department:
            self.department_id = self.department.department_id
        if self.type:
            self.type_id = self.type.positiontype_id
        self.company = self.get_company()
        self.company_id = self.company.company_id
        self.foldergroup = self.get_foldergroup()
        try:
            self.date_posted = parse(timestr=self.data.get('DatePosted', None))
        except:
            self.date_posted = None

    def get_department(self):
        try:
            data = self.data.get('Department', None)
            return Department(data['ID'], data=data)
        except:
            return None

    def contact(self):
        return Contact(self.contact_id)

    def get_company(self):
        try:
            company_id = self.data.get('CompanyID')
            data = {'ID':company_id, 'Name':self.data.get('CompanyName')}
            return Company(company_id=company_id, data=data)
        except:
            return None

    def get_foldergroup(self):
        foldergroup_data = self.data.get('FolderGroup', None)
        try:
            return FolderGroup(foldergroup_id=foldergroup_data['ID'], data=foldergroup_data)
        except:
            return None

    def get_type(self):
        try:
            type_name = (self.data.get('PositionType', None))
            type = get_positiontype_by_name(type_name, data=self.types)
            return type
        except:
            return None

class PostedPosition(Position, object):

    # def refresh(self):
    #     # Hopefully there will be a way to access WebPositionTitle and WebDescription in API 2.0 directly in the future
    #     print(self.data)
    #     self.data = get_position_by_id(self.position_id)
    #     self.populate_from_data()

    def address(self):
        return PostedPositionAddress(data=self.data.get('PrimaryAddress', {}))



    def position(self):
        return self

class PostedPositionAddress(object):
    # PostedPositionAddress is generated from the Position/InternallyPosted api call and the data is different than the
    # standard Address obj in that it cannot be identified by a keyfield
    def __init__(self, data):
        self.data = data
        self.populate_from_data()

    def populate_from_data(self):
        self.address_line_1 = self.data.get('AddressLine1', None)
        self.address_line_2 = self.data.get('AddressLine2', None)
        self.city = self.data.get('City', None)
        self.region = self.data.get('Region', None)
        self.state = self.data.get('State', None)
        self.postal_code = self.data.get('PostalCode', None)
        self.latitude = self.data.get('Latitude', None)
        self.longitude = self.data.get('Longitude', None)

class PositionType(object):
    # 2.0 API
    def __init__(self, positiontype_id, data=None):
        self.positiontype_id = positiontype_id
        if not data:
            # Fetch from remote
            self.refresh()
        else:
            # Allows it to be populated by list methods without an additional fetch
            self.data = data
        self.populate_from_data()

    def refresh(self):
        self.data = get_positiontype_by_id(self.positiontype_id).data
        self.populate_from_data()

    def populate_from_data(self):
        self.name = self.data.get('Name', None)
        self.category_id = self.data.get('CategoryID', None)
        self.subcategory_id = self.data.get('SubCategoryID', None)

def get_position_by_id(position_id):
    connector = ErConnector()  # 2.0 API
    url = 'Position/{id}'.format(
        id=position_id,
    )
    response = connector.send_request(
        path=url,
        verb='GET',
    )

    return Position(response['ID'], data=response)


def list_positions():
    # Currently it is not possible to list all positions. this method is an alias for list_posted_positions
    return list_posted_positions()

def list_posted_positions():
    # 2.0 API
    connector = ErConnector()
    url = 'Position/InternallyPosted'
    response = connector.send_request(
        path=url,
        verb='GET',
    )
    types = list_positiontypes()

    return [PostedPosition(position_id=data['ID'], data=data, types=types) for data in response]

def filter_positions_rest(filter, rawresponse=False, pathonly=False):
    # Using REST API
    connector = ErConnector(api_version='rest')
    querystring = '?'
    for f in filter.keys():
        params = (filter.get(f, None))
        if isinstance(params, str):
            params = [params]
        elif isinstance(params, list):
            pass
        else:
            raise TypeError('Parameters must either be a string or list of values')
        paramlist = []
        for param in params:
            paramlist.append('{key}={value}'.format(key=f, value=param))
        querystring += '&'.join(paramlist)
    path = 'Positions/{entityid}/{filter}'.format(
        filter=querystring,
        entityid=connector.rest_entity_id
    )
    if pathonly:
        return path
    else:
        result = connector.send_request(
            path,
            verb='GET',
            rawresponse=rawresponse
        )
        if rawresponse:
            return result
        else:

            obj_data = {}
            conversion_map = {
                'PositionID':'ID',
                'PositionTitle':'Title',
                'WebPositionTitle': 'WebPositionTitle',
                'WebDescription': 'WebDescription'
            }
            positions = []
            for posdata in result:
                obj_data = {}
                for y in conversion_map.keys():
                    try:
                        obj_data[conversion_map[y]] = (posdata[y])
                    except:
                        pass
                positions.append(Position(obj_data['ID'], data=obj_data))
            return positions

def filter_positions(filter, rawresponse=False, pathonly=False):
    return filter_positions_rest(filter, rawresponse, pathonly)

def get_posted_position_by_id(position_id):
    # 2.0 API
    try:
        return [posted_position for posted_position in list_posted_positions() if posted_position.position_id==position_id][0]
    except Exception as E:
        return E



def get_positiontype_by_id(positiontype_id):
    connector = ErConnector()  # 2.0 API
    url = 'Position/Type/{id}'.format(
        id=positiontype_id,
    )
    response = connector.send_request(
        path=url,
        verb='GET',
    )

    return PositionType(response['ID'], data=response)


def list_positiontypes():
    # 2.0 API
    connector = ErConnector()
    url = 'Position/Type'
    response = connector.send_request(
        path=url,
        verb='GET',
    )
    return [PositionType(positiontype_id=data['ID'], data=data) for data in response]

def get_positiontype_by_name(name, data=None):
    if not data:
        data = list_positiontypes()
    try:
        return [x for x in data if x.name == name][0]
    except:
        return None