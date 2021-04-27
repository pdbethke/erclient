from .base import ErConnector, DataHelper


class Company(DataHelper):

    def __init__(self, company_id, data=None):
        self.company_id = company_id
        if not data:
            # Fetch from remote
            self.refresh()
        else:
            # Allows it to be populated by list_communication_methods without an additional fetch
            self.data = data
            # self.refresh(fetch=False)
        self.populate_from_data()

    def refresh(self):
        self.data = get_company_by_id(self.company_id).data
        self.populate_from_data()

    def populate_from_data(self):
        self.name = self.data.get('Name', None)

    def homepage(self):
        # Part of direct record query, not supplied by positions list.
        response = self.data.get('HomePage', None)
        if not response:
            self.refresh()
        response =  self.data.get('HomePage', None)
        return response


def get_company_by_id(id):
    connector = ErConnector()  # 2.0 API
    url = 'Company/{id}'.format(
        id=id,
    )
    response = connector.send_request(
        path=url,
        verb='GET',
    )

    return Company(response['ID'], data=response)
