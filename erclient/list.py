import random

from .config import client_id, client_secret, token_url, api_base_url
from .base import ErConnector


# Custom Fields

def list_custom_fields(abouttype, indexonly=False):
    mylist = (send_request(
        path='CustomField/{abouttype}/'.format(abouttype=abouttype),
        api_base_url=api_base_url,
        client_id=client_id,
        client_secret=client_secret,
        token_url=token_url))

    if indexonly:
        return [i['Name'] for i in mylist]
    else:
        return mylist


# Generic

def industry_list():
    return (send_request(
        path='Industry/',
        api_base_url=api_base_url,
        client_id=client_id,
        client_secret=client_secret,
        token_url=token_url))

# Communication

def communication_types_list():
    connection = ErConnector()
    return (connection.send_request(
        path='Communication/',
        verb='GET')
    )

def communication_types_category_list():
    return (send_request(
        path='Communication/Category',
        api_base_url=api_base_url,
        client_id=client_id,
        client_secret=client_secret,
        token_url=token_url))


# Address

def address_state_list():
    return (send_request(
        path='Address/State/',
        api_base_url=api_base_url,
        client_id=client_id,
        client_secret=client_secret,
        token_url=token_url))

def address_region_list():
    return (send_request(
        path='Address/Region/',
        api_base_url=api_base_url,
        client_id=client_id,
        client_secret=client_secret,
        token_url=token_url))

def address_country_list():
    return (send_request(
        path='Address/Country/',
        api_base_url=api_base_url,
        client_id=client_id,
        client_secret=client_secret,
        token_url=token_url))

def address_type_list():
    return (send_request(
        path='Address/Type/',
        api_base_url=api_base_url,
        client_id=client_id,
        client_secret=client_secret,
        token_url=token_url))



# Company

def company_status_list():
    return (send_request(
        path='Company/Status/',
        api_base_url=api_base_url,
        client_id=client_id,
        client_secret=client_secret,
        token_url=token_url))

def company_adsource_list():
    return (send_request(
        path='AdSource/Company/',
        api_base_url=api_base_url,
        client_id=client_id,
        client_secret=client_secret,
        token_url=token_url))

# Contact

def contact_status_list():
    return (send_request(
        path='Contact/Status/',
        api_base_url=api_base_url,
        client_id=client_id,
        client_secret=client_secret,
        token_url=token_url))

# Attachment

def attachment_type_list():
    return (send_request(
        path='Attachment/Type',
        api_base_url=api_base_url,
        client_id=client_id,
        client_secret=client_secret,
        token_url=token_url))

#Random

def pick_random(schema, key='ID'):
    num = (random.randint(0, len(schema) - 1))
    pick = schema[num]
    return pick[key]

