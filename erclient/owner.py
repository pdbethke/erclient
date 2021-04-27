from .base import ErConnector
from .recruiter import Recruiter, get_recruiter_by_id

def get_owners(abouttype_id, obj_id, raw=False):

    #Note: An Owner is always a Recruiter, so we return a Recruiter object. It's too much trouble to subclass
    #an Owner Object as Recruiter - Owner is such a thin object, better to assign its parameters to Recruiter

    connector = ErConnector()  # 2.0 API
    url = 'Owner/{abouttype_id}/{obj_id}'.format(
        abouttype_id=abouttype_id,
        obj_id=obj_id
    )
    response = connector.send_request(
        path=url,
        verb='GET',
    )

    #return Recruiter Objects
    if raw:
        return response
    else:
        return [get_recruiter_by_id(x['RecruiterID'], is_primary=x['IsPrimary']) for x in response]

def get_primary_owner(abouttype_id, obj_id):
    try:
        return [x for x in get_owners(abouttype_id, obj_id) if x.is_primary][0]
    except:
        return None

def add_owner(abouttype_id, obj_id, owner_id):
    connector = ErConnector()  # 2.0 API
    url = 'Owner/{abouttype_id}/{obj_id}'.format(
        abouttype_id=abouttype_id,
        obj_id=obj_id
    )
    params = {}
    params['RecruiterID'] = owner_id
    params['AdditionalOwnerTypeID'] = 0
    response = connector.send_request(
        path=url,
        verb='POST',
        payload=params
    )

    return response