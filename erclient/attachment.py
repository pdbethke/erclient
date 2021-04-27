from .base import ErConnector
import mimetypes
from dateutil.parser import parse


class Attachment(object):

    def __init__(self, attachment_id, data=None):
        self.attachment_id = attachment_id
        if not data:
            self.refresh()
        else:
            self.data = data
            self.populate_from_data()

    def __str__(self):
        return self.attachment_id

    def refresh(self):
        self.data = get_remote_attachment(self.attachment_id).data
        self.populate_from_data()

    def populate_from_data(self):
        self.name = self.data.get('Name', None)
        self.version =  self.data.get('Version', None)
        self.type_id = self.data.get('TypeID', None)
        self.type = self.data.get('Type', None)
        self.extension = self.data.get('Extension', None)
        self.is_newest_version = self.data.get('IsNewestVersion', None)
        self.date_added = parse(timestr=self.data.get('DateAdded', None))
        self.about_type = self.data.get('AboutType', None)
        self.description = self.data.get('Description', None)
        self.added_by_id = self.data.get('AddedByID', None)

    def fetch_content(self):
        return get_remote_attachment_content(self.attachment_id).content

    def filename(self):
        return '{Name}'.format(
            Name=self.data.get('Name', None),
        )

    def mimetype(self):
        return '{mimetype}'.format(
            mimetype=mimetypes.guess_type(self.filename())[0]
        )

def get_remote_attachment(attachment_id):
    connector = ErConnector()
    url = 'Attachment/{Id}/'.format(Id=attachment_id)
    response = connector.send_request(
        path=url
    )
    return Attachment(response['ID'], data=response)

def get_remote_attachment_content(attachment_id):
    connector = ErConnector()
    url = 'Attachment/Content/{Id}/'.format(Id=attachment_id)
    response = connector.send_request(
        path=url,
        rawresponse=True
    )
    # return response object.
    return response

def delete_remote_attachment_rest(attachment_id):
    connector = ErConnector(api_version='rest')
    url = '/Attachment/{entityid}/{attachment_id}/Delete/'.format(
        entityid=connector.rest_entity_id,
        attachment_id=attachment_id
    )

    try:
        result = connector.send_request(
            path=url,
            verb='POST',
        )
        # Will raise error if attachment_id does not exist
        return True
    except:
        return False