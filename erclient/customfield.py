from .base import ErConnector
import re

class Customfield(object):

    def __init__(self, custom_field_id, schema=None, abouttype_id=None, obj_id=None, value=None):

        def convert(name):
            s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
            return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

        self.custom_field_id = custom_field_id
        # for obj in schema:
        #     setattr(self, convert(obj), schema[obj])

        self.name = schema['Name']
        self.applies_to = schema['AppliesTo']
        self.field_type = schema['FieldType']
        self.possible_values = schema['PossibleValues']
        if self.possible_values and schema.get('DefaultValue', None) :
            self.possible_values.append(schema.get('DefaultValue'))
        self.remote_list_url = schema['RemoteListUrl']
        self.default_value = schema['DefaultValue']
        self.is_required= schema['IsRequired']
        self.value = value
        self.abouttype_id = abouttype_id
        self.obj_id = obj_id

        if not schema:
            # Fetch from remote
            self.refresh()
        else:
            # Allows it to be populated by list_custom_fields without an additional fetch
            self.schema = schema
            self.refresh(fetch=False)

    def get_is_required(self):
        return self.is_required

    def get_name(self):
        return self.name

    def get_field_type(self):
        return self.field_type

    def set_value_to_default(self):
        self.value = self.default_value

    def set_value(self, value, obj_id, save=True):
        self.obj_id = obj_id
        #enforce value restrictions client-side
        if self.possible_values:
            if value not in self.possible_values:
                raise KeyError('Value "{value}" provided is not one of possible values "{possible_values}" '.format(
                    value=value,
                    possible_values='", "'.join(self.possible_values)
                ))
            else:
                self.value = value
        if save:
            #immediate save
            self.save()
        return self

    def save(self, obj_id=None):
        obj_id = self.obj_id if self.obj_id is not None else obj_id
        if obj_id is None:
            raise Exception('ObjectID Missing for Save Operation')
        url = 'CustomField/{abouttype_id}/{id}/{fieldid}'.format(
            id=obj_id,
            abouttype_id=self.abouttype_id,
            fieldid=self.custom_field_id
        )
        connector = ErConnector()
        payload = {}
        payload['Value'] = self.value
        payload['ID'] = self.custom_field_id
        payload['Name'] = self.name
        response = connector.send_request(
            path=url,
            payload=payload,
            verb='PUT',
        )
        if self.value != response['Value']:
            raise Exception('Custom Field value "{value}" for field "{name}" was not saved remotely'.format(
                    value=self.value,
                    key=self.name,
                ))
        else:
            self.value = response['Value']
        return self

    def refresh(self, fetch=True):
        #ToDo - add refresh code
        pass

def get_remote_customfield_list_for_abouttype(abouttype_id):
    # Get a custom field schema with the provided Id. Optionally return custom fields for a specific record of type
    # abouttype_id
    connector = ErConnector()
    url = 'CustomField/{abouttype_id}/'.format(abouttype_id=abouttype_id)
    response = connector.send_request(
        path=url
    )
    return [Customfield(schema['ID'], schema=schema, abouttype_id=abouttype_id) for schema in response]

def get_remote_customfield_list_for_abouttype_record(abouttype_id, obj_id):
    # Get a custom field schema with the provided Id. Optionally return custom fields for a specific record of type
    # abouttype_id
    abouttype_fields = get_remote_customfield_list_for_abouttype(abouttype_id)
    connector = ErConnector()
    url = 'CustomField/{abouttype_id}/{obj_id}'.format(
        abouttype_id=abouttype_id,
        obj_id=obj_id
    )
    response = connector.send_request(
        path=url
    )
    fields = []
    for x in abouttype_fields:
        try:
            value = (list(y['Value'] for y in response if y['ID'] == x.custom_field_id))[0]
        except:
            value = None
        x.value = value
        fields.append(x)


    return fields

def get_custom_field_by_key(abouttype_id, key, obj_id, value_only=False):
    if obj_id:
        abouttype_fields = get_remote_customfield_list_for_abouttype_record(abouttype_id, obj_id)
    else:
        abouttype_fields = get_remote_customfield_list_for_abouttype(abouttype_id)
    try:
        field = (list(field for field in abouttype_fields if field.name == key))[0]
    except:
        field = None
    if field and value_only:
        return field.value
    else:
        return field
