from functools import lru_cache

from .base import ErConnector
from .customfield import get_custom_field_by_key

gender_choices = [(0, 'Male'), (1, 'Female'), (3, 'Other'), (4, 'Decline') ]
# not in api, convenience #
gender_pronoun_choices = ['he/him/his','she/her/hers','they/them/theirs','ze/zir/zirs', 'ze/hir/hirs']
gender_pronoun_field = 'Pronouns'

class EEOC(object):

    def __init__(self,
                 candidate_id,
                 data=None,
                 ethnicity_list=None,
                 veteran_status_list=None,
                 disability_status_list=None,
                 use_pronouns=False
                 ):
        self.candidate_id = candidate_id
        self.gender_id = None
        self.ethnicity_id = None
        self.veteran_status_id = None
        self.disability_status_id = None
        self.gender = None
        self.use_pronouns = use_pronouns
        self.pronoun = None
        self.disability_status_list = disability_status_list
        self.veteran_status_list = veteran_status_list
        self.ethnicity_list = ethnicity_list
        if not data:
            # Fetch from remote
            self.refresh()
        else:
            # Allows it to be populated by list methods without an additional fetch
            self.data = data
        self.pronoun_field = None
        self.populate_from_data()

    def fetch_and_populate_pronoun_field(self):
        try:
            self.pronoun_field = get_custom_field_by_key('Candidate', 'Pronouns', self.candidate_id)
            self.pronoun = self.pronoun_field.value
        except:
            pass

    def refresh(self):
        self.data = get_candidate_eeoc_by_candidate_id(self.candidate_id).data
        self.populate_from_data()
        if self.use_pronouns:
            self.fetch_and_populate_pronoun_field()

    def populate_from_data(self):
        self.gender_id = self.data.get('Gender', None)
        try:
            self.gender = [x[1] for x in list_choices_gender() if x[0] == self.gender_id][0]
        except:
            pass
        self.ethnicity_id = self.data.get('EthnicityID', None)
        self.veteran_status_id = self.data.get('VeteranStatusID', None)
        self.disability_status_id = self.data.get('DisabilityStatusID', None)

    def ethnicity(self):
        value_list = self.ethnicity_list if self.ethnicity_list else list_choices_ethnicity()
        try:
            return [x[1] for x in value_list if x[0] == self.ethnicity_id][0]
        except:
            return None

    def disability_status(self):
        value_list = self.disability_status_list if self.disability_status_list else list_choices_disability_status()
        try:
            return [x[1] for x in value_list if x[0] == self.disability_status_id][0]
        except:
            return None

    def veteran_status(self):
        value_list = self.veteran_status_list if self.veteran_status_list else list_choices_veteran_status()
        try:
            return [x[1] for x in value_list if x[0] == self.veteran_status_id][0]
        except:
            return None

    def save(self, validate=True):
        connector = ErConnector()  # 2.0 API
        url = 'EEOC/Candidate/{candidate_id}'.format(
            candidate_id=self.candidate_id,
        )
        if validate:
            gender_values = [x[0] for x in list_choices_gender()]
            if self.gender_id and self.gender_id not in gender_values:
                raise AttributeError('Error: Gender must be one of the following values:{values}'.format(values=','.join(gender_values)))
            ethnicity_values = [x[0] for x in (self.ethnicity_list if self.ethnicity_list else list_choices_ethnicity())]
            if self.ethnicity_id and self.ethnicity_id not in ethnicity_values:
                raise AttributeError(
                    'Error: EthnicityID must be one of the following values:{values}'.format(values=','.join([str(x) for x in ethnicity_values])))
            veteran_status_values = [x[0] for x in (self.veteran_status_list if self.veteran_status_list else list_choices_veteran_status())]
            if self.veteran_status_id and self.veteran_status_id not in veteran_status_values:
                raise AttributeError(
                    'Error: VeteranStatusID must be one of the following values:{values}'.format(
                        values=','.join([str(x) for x in veteran_status_values])))
            disability_status_values = [x[0] for x in (
                self.disability_status_list if self.disability_status_list else list_choices_disability_status())]
            if self.disability_status_id and self.disability_status_id not in disability_status_values:
                raise AttributeError(
                    'Error: DisabilityStatusID must be one of the following values:{values}'.format(
                        values=','.join([str(x) for x in disability_status_values])))
        payload = self.data
        payload['Gender'] = self.gender_id
        payload['EthnicityID'] = self.ethnicity_id
        payload['VeteranStatusID'] = self.veteran_status_id
        payload['DisabilityStatusID'] = self.veteran_status_id
        response = connector.send_request(
            path=url,
            verb='PUT',
            payload=payload
        )
        self.refresh()

        return self

def get_candidate_eeoc_by_candidate_id(candidate_id, use_pronouns=False):
    connector = ErConnector()  # 2.0 API
    url = 'EEOC/Candidate/{candidate_id}'.format(
        candidate_id=candidate_id,
    )
    response = connector.send_request(
        path=url,
        verb='GET',
    )
    return EEOC(candidate_id, use_pronouns=use_pronouns, data=response)


def list_choices_gender():
    return gender_choices

def list_choices_ethnicity():
    connector = ErConnector()  # 2.0 API
    url = 'EEOC/Ethnicity'
    try:
        response = connector.send_request(
            path=url,
            verb='GET',
        )
        return [(x['ID'], x['Name']) for x in response] if response else []
    except:
        return []

def list_choices_veteran_status():
    connector = ErConnector()  # 2.0 API
    url = '/EEOC/VeteranStatus'
    try:
        response = connector.send_request(
            path=url,
            verb='GET',
        )
        return [(x['ID'], x['Name']) for x in response] if response else []
    except:
        return []

def list_choices_disability_status():
    connector = ErConnector()  # 2.0 API
    url = '/EEOC/DisabilityStatus'
    try:
        response = connector.send_request(
            path=url,
            verb='GET',
        )
        return [(x['ID'], x['Name']) for x in response] if response else []
    except:
        return []