from functools import lru_cache

from .base import ErConnector

class Department(object):

    def __init__(self, department_id, data=None):
        self.department_id = department_id
        if not data:
            # Fetch from remote
            self.refresh()
        else:
            # Allows it to be populated by list methods without an additional fetch
            self.data = data
        self.populate_from_data()

    def refresh(self):
        self.data = get_department_by_id(self.department_id).data
        self.populate_from_data()

    def populate_from_data(self):
        self.name = self.data.get('Name', None)
        self.parent_id = self.data.get('ParentID', None)

    def parent(self):
        return get_department_by_id(self.parent_id)

def get_department_by_id(department_id):
    connector = ErConnector()  # 2.0 API
    url = 'Department/{id}'.format(
        id=department_id,
    )
    response = connector.send_request(
        path=url,
        verb='GET',
    )

    return Department(department_id, data=response)


def list_departments():
    connector = ErConnector()
    url = 'Department'
    response = connector.send_request(
        path=url,
        verb='GET',
    )
    return [Department(department_id=data['ID'], data=data) for data in response]
