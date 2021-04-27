from .base import ErConnector

class AdSource(object):

    def __init__(self, adsource_id, data=None):
        self.adsource_id = adsource_id
        if not data:
            # Fetch from remote
            self.refresh()
        else:
            # Allows it to be populated by list methods without an additional fetch
            self.data = data
        self.populate_from_data()

    def refresh(self):
        self.data = get_adsource_by_id(adsource_id=self.adsource_id).data
        self.populate_from_data()

    def populate_from_data(self):
        self.name = self.data.get('Name', None)
        self.requires_additional_info = self.data.get('RequiresAdditionalInfo', None)

def list_adsources(abouttype_id):
    # API 2.0
    connector = ErConnector()
    url = 'AdSource/{abouttype_id}/'.format(abouttype_id=abouttype_id)
    response = connector.send_request(
        path=url,
        verb='GET',
    )
    return [AdSource(adsource_id=x['ID'], data=x) for x in response]

def get_adsource_by_id(adsource_id, abouttype_id=None):
    try:
        return [x for x in list_adsources(abouttype_id) if x.adsource_id == adsource_id][0]
    except:
        return None

def get_adsource_id_from_name(name, abouttype_id=None):
    return get_adsource_from_name(name, abouttype_id).adsource_id


def get_adsource_from_name(name, abouttype_id=None):

    return [x for x in list_adsources(abouttype_id) if x.name == name][0]
