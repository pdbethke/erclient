from .base import ErConnector
from .candidate import get_candidate_by_id
from .position import get_position_by_id
from .address import get_address_by_id

class Match(object):

    def __init__(self, match_id, data=None):
        self.match_id = match_id
        if not data:
            # Fetch from remote
            self.refresh()
        else:
            # Allows it to be populated by list methods without an additional fetch
            self.data = data
        self.populate_from_data()

    def refresh(self):
        self.data = get_match_by_id(self.match_id).data

    def populate_from_data(self):
        self.name = self.data.get('Name', None)
        self.candidate_id = self.data.get('CandidateID', None)
        self.position_id = self.data.get('PositionID', None)
        self.default_address_id = self.data.get('DefaultAddressID', None)
        self.status_id = self.data.get('120', None)



    def get_candidate(self):
        return get_candidate_by_id(self.candidate_id)
    def get_position(self):
        return get_position_by_id(self.position_id)
    def get_default_address(self):
        return get_address_by_id(self.default_address_id)

def get_match_by_id(match_id):
    connector = ErConnector()  # 2.0 API
    url = 'Match/{id}'.format(
        id=match_id,
    )
    response = connector.send_request(
        path=url,
        verb='GET',
    )

    return Match(response['ID'], data=response)
