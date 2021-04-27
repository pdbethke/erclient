import csv
import json
import os
import random
from genericpath import exists

from .base import ErConnector
from .address import add_address, get_address_type_id_by_name
from .communication import list_communication_methods, add_communication_method
from .owner import add_owner


class Seed(object):

    def __init__(self, seed_id, data=None):
        self.seed_id = seed_id
        self.data = None
        if not data:
            # Fetch from remote
            self.refresh()
        else:
            # Allows it to be populated by list_communication_methods without an additional fetch
            self.data = data
            self.populate_from_data()

    def refresh(self):
        self.data = get_seed_by_id(self.seed_id).data
        self.populate_from_data()

    def save(self, **kwargs):
        return update_seed(seed_id=self.seed_id, **kwargs)

    def populate_from_data(self):
        self.first_name = self.data.get('First', None)
        self.last_name = self.data.get('Last', None)
        self.full_name = '{first} {last}'.format(
            first=self.first_name,
            last=self.last_name
        )
        self.title = self.data['Title']

    def add_address(self,
                    state_id,
                    type_id=400,
                    address_line_1=None,
                    city=None,
                    region_id=None,
                    postal_code=None,
                    address_line_2=None,
                    country_id=220,
                    default=True
                    ):

        return add_address(abouttype_id='Seed', obj_id=self.seed_id, type_id=type_id, address_line_1=address_line_1, city=city, state_id=state_id,
                           region_id=region_id, postal_code=postal_code, address_line_2=address_line_2,
                           country_id=country_id, default=default)

    def list_communication_methods(self):
        return list_communication_methods('Seed', self.seed_id)

    def add_communication_method(self,type_id, value, is_primary=False):
        return add_communication_method(abouttype_id='Seed', obj_id=self.seed_id, type_id=type_id, value=value, is_primary=is_primary )

    def add_note(self, body, action_id=0):
        # using REST API
        connector = ErConnector(api_version='rest')
        path = 'Seed/{entityid}/{seed_id}/AddNote?ActionID={action_id}'.format(
            entityid=connector.rest_entity_id,
            seed_id=self.seed_id,
            action_id=action_id
        )
        params = {}
        params['CreatedByID'] = connector.api_user_guid_rest
        params['Body'] = body
        params['ActionID'] = action_id
        result = connector.send_request(
            path,
            payload=params,
            verb='POST',rawresponse=True
        )
        return result

    def set_owner(self, owner_id):
        return assign_seed(self.seed_id, owner_id)

def list_seed_fieldinputs():
    out = {}
    out['first_name'] = 'First Name'
    out['last_name'] = 'Last Name'
    out['title'] = 'Title'
    out['company_name'] = 'Company Name'
    out['email'] = 'Email'
    out['phone'] = 'Phone'
    out['address_1'] = 'Address 1'
    out['address_2'] = 'Address 2'
    out['city'] = 'City'
    out['state_id'] = 'State ID'
    out['postal_code'] = 'Postal Code'

    return out

def create_seed(
        type_id,
        expected_harvest_type,
        adsource_id,
        assign_to=0,
        first_name=None,
        last_name=None,
        title=None,
        company_name=None,
        email=None,
        phone=None,
        address_1=None,
        address_2=None,
        city=None,
        state_id=None,
        region_id=None,
        postal_code=None,
        address_type_id=None

):
    connector = ErConnector()
    url = 'Seed/'
    data = {
        'TypeID': type_id,
        'ExpectedHarvestType': expected_harvest_type,
        'AdSourceID': adsource_id,
        'AssignTo': assign_to,
        'First': first_name,
        'Last': last_name,
        'Title': title,
        'CompanyName': company_name,
    }
    response = connector.send_request(
        path=url,
        verb='POST',
        payload=data
    )
    try:
        seed = Seed(seed_id=response['ID'], data=response)
        if email:
            seed.add_communication_method(type_id=200, value=email, is_primary=True)
        if phone:
            seed.add_communication_method(type_id=100, value=phone, is_primary=True)
        if  address_1 and city and state_id and region_id and postal_code:
            if not address_type_id:
                type_id = get_address_type_id_by_name('Main Address')
            else:
                type_id = address_type_id
            seed.add_address(type_id=type_id, address_line_1=address_1, address_line_2=address_2, city=city,
                             state_id=state_id, region_id=region_id, postal_code=postal_code)
        if company_name:
            update_seed(seed.seed_id, CompanyName=company_name)
        seed.refresh()
        return seed
    except Exception as e:
        print(e)
        return e



def update_seed(seed_id, **kwargs):
    seed = get_seed_by_id(seed_id)
    data = seed.data
    for x in kwargs:
        if x in data.keys():
            data[x] = kwargs[x]
    connector = ErConnector()
    url = 'Seed/{seed_id}'.format(seed_id=seed_id)
    response = connector.send_request(
        path=url,
        verb='PUT',
        payload=data,
        rawresponse=True
    )

    return response

def assign_seed(seed_id, user_id):
    connector = ErConnector()
    url = 'Seed/{Id}/AssignTo/{UserId}'.format(Id=seed_id, UserId=user_id)
    response = connector.send_request(
        path=url,
        verb='PATCH',
        rawresponse=True
    )

    return response

def list_seed_types():
    connector = ErConnector()
    url = 'Seed/Type'
    response = connector.send_request(
        path=url,
        verb='GET'
    )

    return response


def get_seed_type_id_by_name(name):
    try:
        return [x for x in list_seed_types() if x['Name'] == name][0]['ID']
    except:
        return None


def get_seed_by_id(id):
    connector = ErConnector()
    url = 'Seed/{id}'.format(id=id)
    response = connector.send_request(
        path=url,
        verb='GET'
    )

    return Seed(seed_id=id, data=response)

def batch_import_from_csv(path):
    with open(path) as csvfile:
        data = [{k: v for k, v in row.items()}
             for row in csv.DictReader(csvfile, skipinitialspace=True)]
    for row in data:
        print(row)

