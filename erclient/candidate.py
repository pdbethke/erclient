from os.path import basename
import datetime
from dateutil.parser import parse
from io import BufferedReader

from .address import Address, get_address_type_id_by_name, get_address_state_id_by_name, get_address_region_id_by_name, \
    list_addresses, get_address_by_id, add_address, get_default_address, delete_address
from .base import ErConnector
from .communication import list_communication_methods, add_communication_method, list_communication_categories
from .config import rest_entity_id
from .customfield import get_remote_customfield_list_for_abouttype, get_remote_customfield_list_for_abouttype_record, \
    get_custom_field_by_key
from .foldergroup import FolderGroup
from .adsource import get_adsource_from_name, get_adsource_id_from_name, get_adsource_by_id
from .owner import get_owners, get_primary_owner
from .seed import create_seed, get_seed_type_id_by_name, update_seed
from .position import get_position_by_id, filter_positions, Position, get_posted_position_by_id
from .attachment import Attachment


class Candidate(object):

    def __init__(self,
                 candidate_id,
                 data=None):
        self.candidate_id = candidate_id
        self.data_orig = {}
        if data:
            # allows obj to be populated by another call that returns a candidate record, eg duplicate/
            self.data = data
            self.data_orig = self.data
        else:
            self.data = get_remote_candidate(candidate_id).data
            self.data_orig = self.data
        self.attribute_map = {
            'first_name': 'First',
            'middle_name': 'Middle',
            'last_name': 'Last',
            'title': 'Title',
            'current_employer': 'CurrentEmployer',
            'is_looking_for_contract': 'IsLookingForContract',
            'is_looking_for_contracttoperm': 'IsLookingForContractToPerm',
            'is_looking_for_perm': 'IsLookingForPerm',
            'status_id': 'StatusID',
            'contractor_type_id': 'ContractorTypeID',
            'user_id': 'UserID'
        }

        self.populate_from_data()

    def __str__(self):
        return self.full_name

    def __getattr__(self, name):
        # Extended calls with 2.0 are expensive. Lets only call them if needed, and still make them appear as class
        # attributes (lazy loading essentially). But for saving we also need to know if a value has been set on
        # the object externally and only then do we save that bit. If we don't we could be re-saving data needlessly
        if name == 'email_address':
            self.email_address = self.get_email_address()
            self.data['EmailAddress'] = self.email_address
            return self.email_address
        elif name == 'main_phone':
            phone = get_candidate_main_phone_number(self.candidate_id)
            if phone:
                self.main_phone = phone.value
                self.data['MainPhone'] = self.main_phone
            else:
                self.main_phone = phone
                self.data['MainPhone'] = phone
            return self.main_phone
        elif name == 'adsource' or name == 'adsource_id':
            self.adsource = self.get_adsource()
            self.adsource_id = int(self.get_adsource_id())
            if name == 'adsource':
                return self.adsource
            else:
                return self.adsource_id
        elif name == 'website':
            try:
                self.website = self.get_default_website().value
            except:
                self.website = None
            return self.website
        elif name == 'default_foldergroup' or name == 'default_foldergroup_id':
            self.default_foldergroup = self.get_default_foldergroup()
            self.default_foldergroup_id = int(self.default_foldergroup.foldergroup_id)
            if name == 'default_foldergroup':
                return self.default_foldergroup
            else:
                return self.default_foldergroup_id
        elif name == 'full_name':
            self.first_name = self.data.get('First', None)
            self.last_name = self.data.get('Last', None)
            self.full_name = '{first} {last}'.format(first=self.first_name, last=self.last_name)
            return self.full_name
        elif name in ['address_line_1', 'address_line_2', 'city', 'state', 'postal_code', 'address']:
            main_address = self.get_address()
            self.data['AddressLine1'] = main_address.address_line_1
            self.data['AddressLine2'] = main_address.address_line_2
            self.data['City'] = main_address.city
            self.data['StateID'] = main_address.state_id
            self.data['PostalCode'] = main_address.postal_code
            self.data['StateName'] = main_address.state_name
            self.data['StateCode'] = main_address.state_code
            self.address = main_address
            if name == 'address':
                return main_address
            else:
                return (main_address.__getattribute__(name))
        else:
            return self.__getattribute__(name)

    def populate_from_data(self):

        for x in self.attribute_map:
            try:
                setattr(self, x, self.data[self.attribute_map[x]])
            except:
                pass
        try:
            self.full_name = '{first} {last}'.format(first=self.first_name, last=self.last_name)
        except:
            self.full_name = '{first}'.format(first=self.first_name,)

    def save(self):
        change_data = {}
        attribute_map = self.attribute_map
        attribute_map['ssn'] = None
        attribute_map.pop('user_id')
        for x in attribute_map:
            try:
                if self.__getattribute__(x) != self.data.get(attribute_map[x]):
                    change_data[attribute_map[x]] = self.__getattribute__(x)
            except:
                pass
        if change_data:
            save_candidate_data(self.candidate_id, change_data)
            self.data = get_remote_candidate(self.candidate_id).data
            self.populate_from_data()
            return self
        else:
            return self

    def get_first_name(self):
        return '{first}'.format(
            first=self.data.get('First', None),
        )

    def get_last_name(self):
        return '{last}'.format(
            last=self.data.get('Last', None)
        )

    def get_full_name(self):
        return '{first} {last}'.format(
            first=self.get_first_name(),
            last=self.get_last_name(),
        )

    def get_email_address(self, as_obj=False):
        obj = get_candidate_primary_email_address(self.candidate_id)
        if as_obj:
            return obj
        else:
            return '{email}'.format(
                email=obj.value,
            )

    def refresh(self):
        self.data = get_remote_candidate(self.candidate_id).data
        self.populate_from_data()

    def list_communication_methods(self, about_id=None, is_primary=False):
        return list_candidate_communication_methods(self.candidate_id, about_id=about_id, is_primary=is_primary)

    def add_communication_method(self, category_id, value, is_primary=False):
        return add_communication_method(
            abouttype_id='Candidate',
            type_id=category_id,
            obj_id=self.candidate_id,
            value=value,
            is_primary=is_primary
        )

    def list_email_addresses(self, as_obj=False):
        # default is to return just the list of addresses, not the object. Returning obj is optional
        obj_list = list_candidate_email_addresses(self.candidate_id)
        if as_obj:
            return obj_list
        else:
            return [x.value for x in obj_list]

    def upload_resume(self, resume, with_copy=True):
        result = upload_resume_to_candidate_profile(self.candidate_id, resume, with_copy=with_copy)
        return result


    def add_note(self, body, action_id=0):
        return add_note_to_candidate(self.candidate_id, body, action_id)

    def add_application(self, position_id, application_source_id, application_note=None):
        return add_candidate_application(self.candidate_id, position_id, application_source_id, application_note=application_note)

    def get_communication_preferences(self, type=None):
        connector = ErConnector()  # 2.0 API
        url = 'Candidate/{id}/CommunicationPreferences'.format(
            type=type,
            id=self.candidate_id
        )
        response = connector.send_request(
            path=url,
            verb='GET',
        )

        return response

    def set_communication_preferences(self, pref_dict):
        connector = ErConnector()  # 2.0 API
        url = 'Candidate/{id}/CommunicationPreferences'.format(
            id=self.candidate_id
        )

        payload = self.get_communication_preferences()
        for x in pref_dict.keys():
            payload[x] = pref_dict[x]

        response = connector.send_request(
            path=url,
            verb='POST',
            payload=payload
        )

        return response

    def list_custom_fields(self):
        return get_remote_customfield_list_for_abouttype_record('Candidate', obj_id=self.candidate_id)

    def get_custom_field(self, key, value_only=False):
        return get_custom_field_by_key('Candidate', key, self.candidate_id, value_only=value_only)

    def get_custom_field_value(self, key):
        return self.get_custom_field(key, value_only=True)

    def save_custom_field_value(self, key, value):
        field = self.get_custom_field(key)
        return field.set_value(value, obj_id=self.candidate_id, save=True)

    def list_main_phone_numbers(self):
        return list_candidate_main_phone_numbers(self.candidate_id)

    def list_references(self):
        return list_candidate_references(self.candidate_id)

    def list_attachments(self):
        return list_candidate_attachments(self.candidate_id, )

    def list_foldergroups(self):
        return list_candidate_foldergroups(self.candidate_id)

    def get_default_foldergroup(self):
        return get_candidate_default_foldergroup(candidate_id=self.candidate_id)

    def list_websites(self):
        return list_candidate_websites(candidate_id=self.candidate_id)

    def get_default_website(self):
        return get_candidate_default_website(candidate_id=self.candidate_id)

    def get_default_address(self):
        return get_candidate_default_addresses(candidate_id=self.candidate_id)

    def do_not_email(self):
        return self.get_communication_preferences()['DoNotEmail']

    def do_not_call(self):
        return self.get_communication_preferences()['DoNotCall']

    def do_not_text(self):
        return self.get_communication_preferences()['DoNotText']

    def set_do_not_email_true(self):
        return self.set_communication_preferences({'DoNotEmail': True})

    def set_do_not_email_false(self):
        return self.set_communication_preferences({'DoNotEmail': False})

    def get_owners(self):
        return get_owners('Candidate', self.candidate_id)

    def get_recruiter(self):
        return get_primary_owner('Candidate', self.candidate_id)

    def get_recruiter_name(self):
        return self.get_recruiter().full_name

    def get_recruiter_guid(self):
        return self.get_recruiter().recruiter_id

    def get_rating(self):
        response = get_candidate_rating(self.candidate_id)
        try:
            return response
        except:
            return None

    def get_adsource(self):
        try:
            return get_adsource_from_name(self.data.get('AdSource', None))
        except:
            return None

    def get_adsource_id(self):
        try:
            return get_adsource_id_from_name(self.data.get('AdSource', None))
        except:
            return None

    def get_address(self):
        try:
            return self.get_default_address()
        except:
            return None

    def add_main_address(self, address_line_1, city, state_id, postal_code, region_id=None):
        address = self.add_address(type_id=400, address_line_1=address_line_1, city=city, state_id=state_id, region_id=None, postal_code=postal_code, default=True)
        return address


    def add_address(self, type_id, address_line_1, city, state_id, region_id, postal_code, default=True):
        result = add_address(
            abouttype_id='Candidate',
            type_id=type_id,
            obj_id=self.candidate_id,
            address_line_1=address_line_1,
            city=city,
            state_id=state_id,
            region_id=region_id,
            postal_code=postal_code,
            default=default

        )
        return result

    def add_contact_reference(self,
                              first_name,
                              last_name,
                              title=None,
                              company_name=None,
                              adsource_id=None,
                              phone=None,
                              email=None,
                              address=None,
                              city=None,
                              state=None,
                              postal_code=None,
                              reference_type=None,
                              reference_text=None,
                              relationship_start_date=None,
                              relationship_end_date=None,
                              rating=None
                              ):
        if not adsource_id:
            adsource_id = 228
        if not reference_type:
            reference_type = 90
        if not rating:
            rating = self.get_rating() or get_candidate_rating_id_by_name('A')

        seed = (
            create_seed(
                type_id=get_seed_type_id_by_name('Reference'),
                expected_harvest_type='Contact',
                adsource_id=adsource_id,
                assign_to=self.get_recruiter().user_id,
                first_name=first_name,
                last_name=last_name,
                title=title,
                company_name=company_name
            )
        )

        # because company_name doesnt seem to save correctly for the creation method

        if company_name:
            update_seed(seed.seed_id, CompanyName=company_name)

        if email:
            seed.add_communication_method(type_id=200, value=email, is_primary=True)

        if phone:
            seed.add_communication_method(type_id=100, value=phone, is_primary=True)
        if address:
            type_id = get_address_type_id_by_name('Main Address')
            seed.add_address(
                type_id=type_id,
                address_line_1=address,
                city=city,
                state_id=get_address_state_id_by_name(state),
                region_id=get_address_region_id_by_name('Metro DC'),
                postal_code=postal_code
            )

        try:
            relationship_start_date = relationship_start_date.strftime('%Y-%m-%dT%H:%M:%S')
        except:
            relationship_start_date = None
        try:
            relationship_end_date = relationship_end_date.strftime('%Y-%m-%dT%H:%M:%S')
        except:
            relationship_end_date = None

        response = add_candidate_reference(
            candidate_id=self.candidate_id,
            reference_type=reference_type,
            reference_id=seed.seed_id,
            reference_text=reference_text,
            name='Reference from {name}'.format(name=seed.full_name),
            relationship_start_date=relationship_start_date,
            relationship_end_date=relationship_end_date,
            rating=rating
        )

        return CandidateReference(candidate_id=self.candidate_id, reference_id=response['ID'], data=response,
                                  candidate=self)

    def list_job_applications(self, extended=False, dedupe=False):
        return list_candidate_applications(self.candidate_id, extended=extended, dedupe=dedupe)


class CandidateApplication(object):

    def __init__(self, application_id, data=None, candidate=None):

        self.application_id = application_id
        self.title = None
        self.position = None
        if not data:
            # Fetch from remote
            self.refresh()
        else:
            self.data = data
            # self.refresh(fetch=False)
        self.populate_from_data()

    def __str__(self):
        return 'Candidate Application for Candidate #{cid} for Position #{pid} on {date}, Adsource: {adsource}, Note: {note}'.format(
            cid=self.candidate_id,
            pid=self.position_id,
            date=self.created_on,
            adsource=self.adsource,
            note=self.note
        )

    def refresh(self):
        self.data = get_candidate_application_by_id(self.application_id)
        self.populate_from_data()

    def get_position(self):
        return get_position_by_id(self.position_id)

    def populate_from_data(self):
        self.position_id = self.data.get('PositionID', None)

        self.candidate_id = self.data.get('CandidateID', None)
        self.status = self.data.get('Status', None)
        self.adsource = self.data.get('AdSource', None)
        self.created_on = parse(timestr=self.data.get('CreatedOn', None))
        self.note = self.data.get('Note', None)
        self.web_position_title = None
        if self.position and isinstance(self.position, Position):
            self.web_position_title = self.position.web_position_title

    def get_application_source(self):
        return get_adsource_from_name(self.adsource)


class CandidateReference(object):

    def __init__(self, candidate_id, reference_id, data=None, candidate=None):

        self.candidate_id = candidate_id
        self.reference_id = reference_id
        if not data:
            # Fetch from remote
            self.refresh()
        else:
            self.data = data
            # self.refresh(fetch=False)
        self.populate_from_data()
        if not candidate:
            self.candidate = Candidate(self.candidate_id)
        else:
            self.candidate = candidate

    def refresh(self):
        self.data = get_candidate_reference_by_id(self.candidate_id, self.reference_id)
        self.populate_from_data()

    def populate_from_data(self):
        self.reference_type = self.data['ReferenceType']
        self.name = self.data['Name']
        self.entered_on = self.data['EnteredOn']
        try:
            self.relationship_start_date = datetime.datetime.strptime(self.data['RelationshipStartDate'],
                                                                      '%Y-%m-%dT%H:%M:%S')
        except:
            self.relationship_start_date = None
        try:
            self.relationship_end_date = datetime.datetime.strptime(self.data['RelationshipEndDate'],
                                                                    '%Y-%m-%dT%H:%M:%S')
        except:
            self.relationship_end_date = None
        self.reference_text = get_candidate_reference_text_by_reference_id(self.reference_id)


class CandidateReferenceImportSet(object):
    def __init__(self, candidate, references):
        self.candidate = candidate
        self.references = references


def save_candidate_data(candidate_id, data):
    # API 2.0
    valid_data = [
        "First",
        "Last",
        "Middle",
        "Title",
        "CurrentEmployer",
        "IsLookingForContract",
        "IsLookingForContractToPerm",
        "IsLookingForPerm",
        "StatusID",
        "SSN",
        "ContractorTypeID"
    ]
    connector = ErConnector()
    url = '/Candidate/{id}'.format(id=candidate_id)
    payload = {}
    for x in data:
        if x in valid_data:
            payload[x] = data[x]
    response = connector.send_request(
        path=url,
        verb='PUT',
        payload=data
    )

    return response


def list_candidate_references(candidate_id):
    # API 2.0
    connector = ErConnector()
    url = 'CandidateReference/{candidate_id}/'.format(candidate_id=candidate_id)
    response = connector.send_request(
        path=url
    )
    return [CandidateReference(candidate_id=reference['CandidateID'], reference_id=reference['ID'], data=reference) for
            reference in response]


def get_candidate_application_by_id(application_id):
    # API 2.0
    connector = ErConnector()
    url = 'CandidateApplication/{Id}/'.format(Id=application_id)
    response = connector.send_request(
        path=url
    )
    return CandidateApplication(application_id, data=response)


def get_candidate_reference_by_id(candidate_id, reference_id):
    # API 2.0
    try:
        return \
            [reference for reference in list_candidate_references(candidate_id) if
             reference.reference_id == reference_id][
                0]
    except:
        return None


def add_candidate_reference(candidate_id, reference_type, reference_id, reference_text, name,
                            relationship_start_date=None, relationship_end_date=None, rating=0):
    # API 2.0
    connector = ErConnector()
    url = '/CandidateReference/'
    data = {}
    data['CandidateID'] = candidate_id
    data['ReferenceType'] = reference_type  # ie "Seed"
    data['ReferenceID'] = reference_id  # id of the Seed
    data['ReferenceText'] = reference_text
    data['Name'] = name
    data['RelationshipStartDate'] = relationship_start_date
    data['RelationshipEndDate'] = relationship_end_date
    data['Rating'] = rating
    response = connector.send_request(
        path=url,
        verb='POST',
        payload=data
    )

    return response


def get_candidate_reference_text_by_reference_id(reference_id):
    # API 2.0
    connector = ErConnector()
    url = '/CandidateReference/{Id}/Text'.format(Id=reference_id)
    response = connector.send_request(
        path=url,
        verb='GET',
    )
    try:
        return response['Text']
    except:
        return None


def add_candidate_application(candidate_id, position_id, application_source_id, application_note=None):
    # API 2.0
    connector = ErConnector()
    url = '/CandidateApplication/'
    data = {}
    data['CandidateID'] = candidate_id
    data['PositionID'] = position_id  # ie "Seed"
    data['ApplicationSourceID'] = application_source_id  # id of the Seed
    data['ApplicationNote'] = application_note
    response = connector.send_request(
        path=url,
        verb='POST',
        payload=data
    )

    return CandidateApplication(application_id=response['ID'], data=response)


def candidate_schema(schema):
    schema.pop('_expanded', None)
    schema.pop('_links', None)
    return schema


def list_candidate_custom_fields(indexonly=False):
    return get_remote_customfield_list_for_abouttype('Candidate')


def get_remote_candidate(candidate_id):
    # API 2.0
    connector = ErConnector()
    url = 'Candidate/{candidate_id}/'.format(candidate_id=candidate_id)
    response = connector.send_request(
        path=url
    )
    return Candidate(candidate_id=response['ID'], data=response)


def list_candidate_communication_methods(candidate_id, about_id=None, is_primary=False):
    # API 2.0
    return list_communication_methods('Candidate', candidate_id, about_id=about_id, is_primary=is_primary)


def list_candidate_email_addresses(candidate_id):
    # API 2.0
    return list_candidate_communication_methods(candidate_id, about_id=200)


def list_candidate_main_phone_numbers(candidate_id):
    # API 2.0
    return list_candidate_communication_methods(candidate_id, about_id=100)


def get_candidate_main_phone_number(candidate_id):
    # API 2.0
    try:
        return [x for x in list_candidate_main_phone_numbers(candidate_id) if x.is_primary][0]
    except:
        return None


def list_candidate_addresses(candidate_id):
    # API 2.0
    return list_addresses('Candidate', candidate_id)


def get_candidate_default_addresses(candidate_id):
    # API 2.0
    return get_default_address('Candidate', candidate_id)


def get_candidate_primary_email_address(candidate_id):
    # API 2.0
    try:
        return [x for x in list_candidate_email_addresses(candidate_id) if x.is_primary][0]
    except:
        return None


def get_candidate_rating(candidate_id):
    # API 2.0
    connector = ErConnector()
    url = 'Candidate/Rating/{candidate_id}/'.format(candidate_id=candidate_id)
    response = connector.send_request(
        path=url
    )
    try:
        return get_candidate_rating_name_by_id(response['ID'])
    except:
        return None


def list_candidate_ratings():
    # API 2.0
    connector = ErConnector()
    url = 'Candidate/Rating/'
    response = connector.send_request(
        path=url
    )
    return response


def list_candidate_attachments(candidate_id, ):
    connector = ErConnector()  # 2.0 API
    url = 'Attachment/Candidate/{Id}'.format(
        Id=candidate_id
    )
    response = connector.send_request(
        path=url,
        verb='GET',
    )
    return [Attachment(attachment_id=attachment['ID'], data=attachment) for
            attachment in response]


def list_candidate_applications(candidate_id, extended=False, dedupe=False):
    connector = ErConnector()  # 2.0 API
    url = 'CandidateApplication/Candidate/{Id}'.format(
        Id=candidate_id
    )
    response = connector.send_request(
        path=url,
        verb='GET',
    )
    apps = [CandidateApplication(application_id=application['ID'], data=application) for
            application in response]
    if extended and apps:
        pids = [application['PositionID'] for application in response]
        ext_data = filter_positions({'PositionID': pids})
        pos_dict = {}
        for x in ext_data:
            pos_dict[int(x.position_id)] = x
        for app in apps:
            try:
                app.position = (pos_dict[app.position_id])
                app.populate_from_data()
            except:
                pass
        apps = sorted(apps, key=lambda x: x.created_on, reverse=True)

    try:
        if dedupe and apps:
            out = []
            pids = []
            for app in apps:
                if app.position_id not in pids:
                    out.append(app)
                    pids.append(app.position_id)
            apps = out
    except:
        pass

    return apps


def list_candidate_foldergroups(candidate_id):
    connector = ErConnector()  # 2.0 API
    url = 'FolderGroup/{AboutType}/{Id}'.format(
        AboutType='Candidate',
        Id=candidate_id
    )
    response = connector.send_request(
        path=url,
        verb='GET',
    )

    return [FolderGroup(foldergroup_id=foldergroup['ID'], data=foldergroup) for
            foldergroup in response]


def get_candidate_default_foldergroup(candidate_id):
    connector = ErConnector()  # 2.0 API
    url = 'FolderGroup/{AboutType}/{Id}/Default'.format(
        AboutType='Candidate',
        Id=candidate_id
    )
    response = connector.send_request(
        path=url,
        verb='GET',
    )

    # return [FolderGroup(foldergroup_id=foldergroup['ID'], data=foldergroup) for
    #         foldergroup in response]

    try:
        return FolderGroup(foldergroup_id=response['ID'], data=response)
    except:
        return None


def list_candidate_websites(candidate_id, is_primary=False):
    return list_communication_methods('Candidate', candidate_id, about_id=300, is_primary=is_primary)


def get_candidate_default_website(candidate_id):
    try:
        return list_candidate_websites(candidate_id, is_primary=True)[0]
    except:
        return None


def get_candidate_rating_id_by_name(name):
    # API 2.0
    try:
        return [x for x in list_candidate_ratings() if x['Name'] == name][0]['ID']
    except:
        return None


def get_candidate_rating_name_by_id(id):
    # API 2.0
    try:
        return [x for x in list_candidate_ratings() if x['ID'] == id][0]['Name']
    except:
        return None


def add_note_to_candidate(candidate_id, body, action_id=0):
    # using REST API
    connector = ErConnector(api_version='rest')
    path = 'Candidate/{entityid}/{candidate_id}/AddNote?ActionID={action_id}'.format(
        entityid=connector.rest_entity_id,
        candidate_id=candidate_id,
        action_id=action_id
    )
    params = {}
    params['CreatedByID'] = connector.api_user_guid_rest
    params['Body'] = body
    params['ActionID'] = action_id
    return connector.send_request(
        path,
        payload=params,
        verb='POST',
    )['Message']


def upload_attachment_to_candidate_profile(candidate_id, file, type_id):
    # using REST uploader
    connector = ErConnector(api_version='rest')
    path = 'Attachment/Do/UploadAttachment/'
    try:
        name = basename(file)
    except TypeError:
        name = basename(file.name)
    params = {}
    params['ReferenceID'] = candidate_id
    params['CreatedByID'] = connector.api_user_guid_rest
    params['AttachmentTypeID'] = type_id
    params['Name'] = name
    params['AboutTypeID'] = 6
    params['EntityID'] = rest_entity_id
    files = {}
    files['file'] = file
    return connector.send_request(
        path,
        payload=params,
        file=file,
        verb='POST',
    )['Message']


def upload_resume_to_candidate_profile(
        candidate_id,
        file,
        make_default=True,
        with_copy=True,
        parse_skills=False,
        replace_skills=False,
        update_contact_inf0=False
):
    # Use 1.0 attachment uploader for resume and return attachment_id
    connector = ErConnector(api_version='rest')
    path = 'Candidate/{EntityID}/{CandidateID}/UploadResume/'.format(
        EntityID=rest_entity_id,
        CandidateID=candidate_id,
        CreatorGUID=connector.api_user_guid_rest
    )
    params = {}
    params['ChangedByID'] = connector.api_user_guid_rest
    params['CreatedByID'] = connector.api_user_guid_rest
    params['IsDefaultResume'] = make_default
    params['ParseSkills'] = parse_skills
    params['ReplaceSkills'] = replace_skills
    params['UpdateContactInfo'] = update_contact_inf0
    result = connector.send_request(
        path,
        payload=params,
        file=file,
        verb='POST',
    )
    attachment_id = result['Message']
    if with_copy:
        attachment_id = upload_attachment_to_candidate_profile(candidate_id, file, type_id=1)
    return attachment_id

    # New better way to do it
    # return upload_attachment_to_candidate_profile(candidate_id, file, type_id=1)


def import_resume_from_attachment(
        candidate_id,
        attachment_id,
        replace_contact_info=False,
        update_employment='Update',
        update_education='Update',
        update_skills='Update'

):
    # Use 2.0 parser on an existing attachment. Do not replace contact info is default but can be changed.
    path = '/Candidate/{Id}/Resume/Attachment/{AttachmentID}/?replaceContactInfo={replace_contact_info}' \
           '&updateEmployment={update_employment}&updateEducation={update_education}&updateSkills={update_skills}' \
        .format(
        Id=candidate_id,
        AttachmentID=attachment_id,
        replace_contact_info=str(replace_contact_info),
        update_employment=update_employment,
        update_education=update_education,
        update_skills=update_skills
    )
    connector = ErConnector()
    payload = {
        'replaceContactInfo': replace_contact_info,
        'updateEmployment': update_employment,
        'updateEducation': update_education,
        'updateSkills': update_skills

    }

    response = connector.send_request(
        path=path,
        payload=payload,
        verb='PUT',
    )
    return response

def list_duplicates(first=None, last=None, middle=None, emails=None, phones=None):
    # API 2.0
    connector = ErConnector()
    url = 'Candidate/Duplicate'
    payload = {
        'First': first,
        'Last': last,
        'Middle': middle,
        'Emails': emails,
        'Phones': phones,
    }
    response = connector.send_request(
        path=url,
        payload=payload,
        verb='POST'
    )
    return [Candidate(candidate_id=can['ID'], data=can) for can in response]

class ApplicationException(BaseException):
    pass

class ApplicationExtendedException(BaseException):
    pass


def create_candidate_rest(
        first,
        last,
        title,
        folder_group_id,
        adsource,
        email_address,
        phone_number,
        password,
        ad_source_additional_info=None,
        middle=None,
        ssn=None,
        address_1=None,
        address_2=None,
        city=None,
        state_id=None,
        postal_code=None,
        portfolio_url=None,
        resume=None,
        position_id=None,
        position_source=None,
        position_vendor=None
):
    # using REST API. Optionally setting Password value
    connector = ErConnector(api_version='rest')
    path = '/Candidate/Do/Create'

    if position_id:
        position = get_posted_position_by_id(position_id)
        owner_id = position.primary_owner_id
    else:
        position = None
        owner_id = connector.api_user_guid_rest

    if adsource.requires_additional_info and not ad_source_additional_info:
        ad_source_additional_info = ''

    # Phase 1 processing #
    postparams = {}
    postparams['Email'] = email_address
    postparams['Password'] = password
    postparams['FirstName'] = first
    postparams['LastName'] = last
    postparams['CreatedByID'] = connector.api_user_guid_rest
    postparams['EntityID'] = connector.rest_entity_id
    postparams['OwnerID'] = owner_id
    postparams['FolderGroupID'] = folder_group_id
    postparams['Title'] = title
    postparams['AdSource'] = adsource.name
    postparams['AdsourceAdditionalInfo'] = ad_source_additional_info
    postparams['AddressLine1'] = address_1
    postparams['City'] = city
    postparams['StateID'] = state_id
    postparams['PostalCode'] = postal_code,
    postparams['CommunicationMethod_100'] = phone_number,
    if portfolio_url is not None:
        postparams['CommunicationMethod_300'] = portfolio_url
    postparams['WithPermissions'] = 'Yes'
    postparams['CheckforDup'] = 'Yes'
    postparams['IsApproved'] = 'Yes'
    files = {}
    files['ResumeFile'] = resume
    try:
        result = connector.send_request(
            path,
            payload=postparams,
            file=resume,
            verb='POST',
        )
    except Exception as e:
        # Initial creation fails in the API or there is missing data. We abort
        error = 'Step 1 processing failed for email address {email}: {error}'.format(
            email=email_address,
            error=e
        )

        raise ApplicationException(error)

    # Phase 2 - we validate that a candiateID has been generated: #

    try:
        candidate_id = result['Message']
    except AttributeError:
        error = 'Step 2 processing failed for email address {email}: A valid CandidateID was not returned.'.format(
            email=email_address
        )
        raise ApplicationException(error)

    # Step 3 - we validate the candidate can login #

    try:
        candidate = (validate_rest(email_address, password))
        if not candidate:
            error = 'Step 3 processing failed for CandidateID {cid}: A profile was created but does not validate ' \
                    'against credentials.'.format(
                cid=candidate_id
            )
            raise ApplicationExtendedException(error)
    except Exception as e:
        # Initial creation fails in the API or there is missing data. We abort
        error = 'Step 3 processing failed for CandidateID {cid}: A profile was created but validation ' \
                'failed: {error}'.format(cid=candidate_id, error=e)
        raise ApplicationExtendedException(error)



    # Step 4 - correct resume address overwriting #

    try:
        def address_changed(address, address_1, city, state_id, postal_code):
            try:
                if address.address_line_1 != address_1 or address.city != city or int(address.state_id) != int(
                        state_id) or address.postal_code != postal_code:
                    return True
                else:
                    return False
            except:
                return True
        candidate_address = candidate.address
        if resume and address_changed(candidate.address, address_1, city, state_id, postal_code):
            # account for resume parsing
            if candidate_address and isinstance(candidate_address, Address):
                candidate_address.delete()
            candidate.add_main_address(address_1, city,state_id,postal_code)
    except Exception as e:
        # Initial creation fails in the API or there is missing data. We abort
        error = 'Step 4 processing failed for CandidateID {cid}: A profile was created but with ' \
                'an error in the address re-parsing stage: {error}'.format(cid=candidate_id, error=e)
        raise ApplicationExtendedException(error)

    try:
        if candidate.main_phone != phone_number:
            # resume parsing screwed up phone number
            for x in (candidate.list_main_phone_numbers()):
                if x.value == phone_number:
                    x.delete()
                    candidate.add_communication_method(category_id=100, value=phone_number, is_primary=True)
                    break
    except Exception as e:
        # Initial creation fails in the API or there is missing data. We abort
        error = 'Step 5 processing failed for CandidateID {cid}: A profile was created but with ' \
                'an error in the phone re-parsing stage: {error}'.format(cid=candidate_id, error=e)
        raise ApplicationExtendedException(error)

    try:
        if position:
            if not position_source:
                position_source = adsource
            candidate.add_application(position.position_id, position_source.adsource_id, position_vendor)
    except Exception as e:
        error = 'Step 6 processing failed for CandidateID {cid}: A profile was created but with ' \
                'an error in the position application stage: {error}'.format(cid=candidate_id, error=e)
        raise ApplicationExtendedException(error)
    try:
        if resume:
                #upload duplicate
                upload_attachment_to_candidate_profile(
                    candidate.candidate_id,
                file=resume,
                type_id=1)
    except Exception as e:
        error = 'Step 7 processing failed for CandidateID {cid}: A profile was created but with ' \
                'an error in the resume copy upload stage: {error}'.format(cid=candidate_id, error=e)
        raise ApplicationExtendedException(error)

    return candidate

def create_candidate(
        first,
        last,
        title,
        folder_group_id,
        adsource_id,
        email_address,
        phone_number,
        password,
        ad_source_additional_info=None,
        middle=None,
        ssn=None,
        address_1=None,
        address_2=None,
        city=None,
        state_id=None,
        postal_code=None,
        portfolio_url=None,
        resume=None,
        position=None):
    # API 2.0
    connector = ErConnector()
    url = 'Candidate/'

    payload = {
        'First': first,
        'Last': last,
        'Middle': middle,
        'Title': title,
        'FolderGroupID': folder_group_id,
        'AdSourceID': adsource_id,
        'AdSourceAdditionalInfo': ad_source_additional_info,
        'Emails': [email_address],
        'Phones': [phone_number],
        'SSN': ssn
    }
    try:
        response = connector.send_request(
            path=url,
            payload=payload,
            verb='POST'
        )
        candidate = Candidate(candidate_id=response['ID'], data=response)
        if resume:
            candidate.upload_resume(resume)

        if address_1 and city and state_id and postal_code:
            type_id = get_address_type_id_by_name('Main Address')
            region_id = None
            address=candidate.add_address(
                type_id=type_id,
                address_line_1=address_1,
                city=city,
                region_id=region_id,
                state_id=state_id,
                postal_code=postal_code
            )
            # Set this as the default address, replacing one that might have been added by resume parsing
            update_candidate_default_address(candidate_id=candidate.candidate_id, address_id=address.address_id)
        if portfolio_url:
            candidate.add_communication_method(category_id=300, value=portfolio_url, is_primary=True)

        # provision candidate using REST - which is less fussy

        change_password_rest(
            candidate_id=candidate.candidate_id,
            newpassword=password,
            email_address=email_address
        )

        candidate.refresh()
        #
        # # account for overwrites by the resume processor
        # if candidate.main_phone != phone_number or candidate.email_address != email_address:
        #     if candidate.main_phone != phone_number:
        #         candidate.add_communication_method(category_id=100, value=phone_number, is_primary=True)
        #     if candidate.email_address != email_address:
        #         candidate.add_communication_method(category_id=200, value=email_address, is_primary=True)
        #     candidate.refresh()
        return candidate
    except:
        return response


def get_candidate_rest_xml(candidate_id):
    # Use 1.0 api to grab candidate xml OBJ to get certain values not implemented yet in 2.0 API
    connector = ErConnector(api_version='rest')
    path = 'Candidate/{EntityID}/{CandidateID}/'.format(
        EntityID=rest_entity_id,
        CandidateID=candidate_id,
    )
    response = connector.send_request(
        path=path,
        verb='GET'
    )

    try:
        return response['Data']['Candidate']
    except:
        return None


def provision_candidate(candidate_id, password):
    connector = ErConnector()
    url = '/Candidate/{Id}/Provision'.format(Id=candidate_id)
    payload = {
        'Password': password,
        'EmailConfirmation': False,
        'WithPermissions': True,
    }
    response = connector.send_request(
        path=url,
        payload=payload,
        verb='POST'
    )
    return response


def validate_rest(username, password):
    # using REST API. If valid, returns Candidate object. If not, returns False
    connector = ErConnector(api_version='rest')
    path = 'User/Validate?UserName={UserName}&Password={Password}&EntityID={EntityID}'.format(
        UserName=username,
        Password=password,
        EntityID=connector.rest_entity_id
    )
    params = {}
    params['UserName'] = username
    params['Password'] = password
    params['EntityID'] = connector.rest_entity_id
    try:
        result = (connector.send_request(
            path,
            payload=params,
            verb='POST',
        ))
        return Candidate(result['ReferenceID'])
    except Exception as e:
        return False


def convert_rest_candidate_data_to_candidate(rest_data):
    conversion_map = {

        'FirstName': 'First',
        'LastName': 'Last',
        'MiddleName': 'Middle',
        'NickName': 'NickName',
        'Title': 'Title',
        'AdSource': 'AdSource',
        'CandidateID': 'ID',
        'UserID': 'UserID',
        'IsLookingForPerm': 'IsLookingForPerm',
        'IsLookingForContract': 'IsLookingForContract',
        'IsLookingForContractToPerm': 'IsLookingForContractToPerm',
        'StatusID': 'StatusID',
        'AddressID': 'DefaultAddressID',
        'RatingID': 'RatingID'

    }
    data = {}
    for x in conversion_map.keys():
        sourcefield = x
        targetfield = (conversion_map[x])
        try:
            data[targetfield] = rest_data[sourcefield]
        except:
            data[targetfield] = None
    data['AboutType'] = 'Candidate'
    data['EducationLeveID'] = None
    data['ContratorTypeID'] = None
    data['CurrentEmployer'] = None
    data['_links'] = []
    try:
        return Candidate(data['ID'], data=data)
    except Exception as e:
        return e

import json
def lookup_rest(email):
    # using REST API.
    connector = ErConnector(api_version='rest')
    path = 'User/{entityid}/{email}'.format(
        email=email,
        entityid=connector.rest_entity_id
    )
    result = connector.send_request(
        path,
        verb='GET',

    )
    if isinstance(result, str):
        raise Exception('The email address "{email}" is incompatible with the eRecruit API'.format(email=email))
    else:
        try:
            result = convert_rest_candidate_data_to_candidate(result[0])
            if isinstance(result, Candidate):
                return result
            else:
                return False
        except:
            return False


def get_candidate_data_rest(candidate_id):
    # using REST API.
    connector = ErConnector(api_version='rest')
    path = 'Candidate/{entityid}/{candidateid}'.format(
        candidateid=candidate_id,
        entityid=connector.rest_entity_id
    )
    result = connector.send_request(
        path,
        verb='GET',
        rawresponse=False
    )
    return result[0]


def list_candidate_custom_fields_rest(candidate_id, conversion_map=None, return_map_only=False):
    # using REST API.
    connector = ErConnector(api_version='rest')
    cfields = get_candidate_data_rest(candidate_id)['CustomFieldValues']
    out = []
    data = connector.convert_xml_to_json(cfields)
    for x in data:
        elem = {}
        for y in x.keys():
            val = x[y]
            if conversion_map and conversion_map.get(y, None):
                elem[conversion_map.get(y, None)] = val
                out.append(elem)
            else:
                if conversion_map and return_map_only:
                    pass
                else:
                    elem[y] = val
                    out.append(elem)
    return out

def delete_candidate_custom_field_rest(candidate_id, field_name):
    value = get_custom_field_value_id_rest(candidate_id, field_name)
    if value:
        connector = ErConnector(api_version='rest')
        path = 'CustomField/{entityid}/{customvalueid}/Delete'.format(
            entityid=connector.rest_entity_id,
            customvalueid=value,
        )
        params = {}
        return connector.send_request(
            path,
            payload=params,
            verb='POST',
        )['Message']
    else:
        return None

def get_custom_field_value_id_rest(candidate_id, field_name):
    try:
        fields = (list_candidate_custom_fields_rest(candidate_id))
        value = ([x for x in fields if (x['@Name'] == field_name)][0]['@ValueID'])
        if int(value) > 0:
            return int(value)
        else:
            return None
    except Exception as e:
        return None

def parse_rest_result(result):
    parsed = str(result['Message']).split('|')
    return parsed[0], parsed[1]


def change_password_rest(candidate_id, newpassword, email_address=None, note=None):
    # using REST API. Optionally setting Login value
    connector = ErConnector(api_version='rest')
    candidate = Candidate(candidate_id)
    path = 'Candidate/{entityid}/{candidateid}/Update/'.format(
        candidateid=candidate_id,
        entityid=connector.rest_entity_id
    )
    params = {}
    if email_address:
        params['Email'] = email_address
    else:
        params['Email'] = candidate.email_address
    params['Password'] = newpassword
    params['WithPermissions'] = True
    params['ChangedByID'] = connector.api_user_guid_rest
    result = connector.send_request(
        path,
        payload=params,
        verb='POST',
    )

    status = int(parse_rest_result(result)[0])
    message = parse_rest_result(result)[0]
    if status == 100 and note:
        candidate.add_note(note)
    return message

def change_login_rest(candidate_id, newlogin, note=None):
    # using REST API. Optionally setting Password value
    connector = ErConnector(api_version='rest')
    candidate = Candidate(candidate_id)
    path = 'Candidate/{entityid}/{candidateid}/Update/'.format(
        candidateid=candidate_id,
        entityid=connector.rest_entity_id
    )
    params = {}
    params['Email'] = newlogin
    params['WithPermissions'] = True
    params['ChangedByID'] = connector.api_user_guid_rest
    result = connector.send_request(
        path,
        payload=params,
        verb='POST',
    )
    status = int(parse_rest_result(result)[0])
    message = parse_rest_result(result)[0]
    if status == 100 and note:
        candidate.add_note(note)
    return candidate

def update_candidate_default_address(candidate_id, address_id):
    connector = ErConnector()
    url = 'Address/Candidate/{Id}/Default/{address_id}'.format(
        Id=candidate_id,
        address_id=address_id)

    response = connector.send_request(
        path=url,
        verb='PATCH'
    )
    return response