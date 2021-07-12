import random

from .config import client_id, client_secret, token_url, api_base_url
from .base import ErConnector

# Communication

def communication_types_list():
    connection = ErConnector()
    return (connection.send_request(
        path='Communication/',
        verb='GET')
    )

#Random

def pick_random(schema, key='ID'):
    num = (random.randint(0, len(schema) - 1))
    pick = schema[num]
    return pick[key]

