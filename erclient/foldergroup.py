from .base import ErConnector

class FolderGroup(object):

    def __init__(self, foldergroup_id, data=None):
        self.foldergroup_id = foldergroup_id
        if not data:
            # Fetch from remote
            self.refresh()
        else:
            # Allows it to be populated by list methods without an additional fetch
            self.data = data
        self.populate_from_data()

    def refresh(self):
        self.data = get_foldergroup_by_id(self.foldergroup_id).data

    def populate_from_data(self):
        self.name = self.data.get('Name', None)
        self.category_id = self.data.get('CategoryID', None)
        self.subcategory_id = self.data.get('SubcategoryID', None)
        if not self.subcategory_id:
            # list positions returns this data differently. Arg...
            self.subcategory_id = self.data.get('SubCategoryID', None)

    def get_category(self):
        return FolderGroupCategory(category_id=self.category_id)
    def get_subcategory(self):
        return FolderGroupSubCategory(subcategory_id=self.subcategory_id)

def get_foldergroup_by_id(foldergroup_id):
    connector = ErConnector()  # 2.0 API
    url = 'FolderGroup/{id}'.format(
        id=foldergroup_id,
    )
    response = connector.send_request(
        path=url,
        verb='GET',
    )

    return FolderGroup(response['ID'], data=response)


def list_foldergroups(category_id=None, subcategory_id=None):
    connector = ErConnector()
    url = 'FolderGroup/'
    urls = []
    if category_id is not None:
        try:
            cats = [str(cat) for cat in category_id]
            urls.append('CategoryId=' + ','.join(cats))
        except:
            urls.append('CategoryId=' + str(category_id))

    if subcategory_id is not None:
        try:
            subcats = [str(subcat) for subcat in subcategory_id]
            urls.append('SubCategoryId=' + ','.join(subcats))
        except:
            urls.append('SubCategoryId=' + str(subcategory_id))
    if urls:
        url = url + '?' + '&'.join(urls)
    response = connector.send_request(
        path=url,
        verb='GET',
    )

    return [FolderGroup(foldergroup_id=data['ID'], data=data) for data in response]

def set_candidate_default_foldergroup(candidate_id, foldergroup_id):
    connector = ErConnector()  # 2.0 API
    url = '/FolderGroup/Candidate/{Id}/Default/{FolderGroupId}'.format(
        Id=candidate_id,
        FolderGroupId=foldergroup_id
    )
    response = connector.send_request(
        path=url,
        verb='PATCH',
        rawresponse=True
    )

    return response

class FolderGroupSubCategory(object):

    def __init__(self, subcategory_id, data=None):
        self.subcategory_id = subcategory_id
        if not data:
            # Fetch from remote
            self.refresh()
        else:
            # Allows it to be populated by list methods without an additional fetch
            self.data = data
        self.populate_from_data()

    def refresh(self):
        self.data = get_subcategory_by_id(self.subcategory_id).data
        self.populate_from_data()

    def populate_from_data(self):
        self.name = self.data.get('Name', None)

def get_subcategory_by_id(subcategory_id):
    connector = ErConnector()  # 2.0 API
    url = 'FolderGroup/SubCategory/{id}'.format(
        id=subcategory_id,
    )
    response = connector.send_request(
        path=url,
        verb='GET',
    )

    return FolderGroupSubCategory(response['ID'], data=response)


def list_subcategories(raw=False):
    # 2.0 API
    connector = ErConnector()
    url = 'FolderGroup/SubCategory/'
    if raw:
        response = connector.send_request(
            path=url,
            verb='GET',
            rawresponse=True
        )

        return response

    else:
        response = connector.send_request(
            path=url,
            verb='GET',
        )
        return [FolderGroupSubCategory(subcategory_id=data['ID'], data=data) for data in response]

class FolderGroupCategory(object):

    def __init__(self, category_id, data=None):
        self.category_id = category_id
        if not data:
            # Fetch from remote
            self.refresh()
        else:
            # Allows it to be populated by list methods without an additional fetch
            self.data = data
        self.populate_from_data()

    def refresh(self):
        self.data = get_category_by_id(self.category_id).data
        self.populate_from_data()

    def populate_from_data(self):
        self.name = self.data.get('Name', None)

def get_category_by_id(category_id):
    connector = ErConnector()  # 2.0 API
    url = 'FolderGroup/Category/{id}'.format(
        id=category_id,
    )
    response = connector.send_request(
        path=url,
        verb='GET',
    )

    return FolderGroupCategory(response['ID'], data=response)


def list_categories():
    connector = ErConnector()
    url = 'FolderGroup/Category/'
    response = connector.send_request(
        path=url,
        verb='GET',
    )
    return response

