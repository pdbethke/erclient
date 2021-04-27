from datetime import datetime, timedelta
from xml.dom import minidom
from xml.etree import ElementTree as ET

import requests

from .candidate import Candidate
from .config import estaff_base_url, estaff_api_base_url, estaff_username, estaff_password, reference_note_boilerplate


class xmlHelper(object):

    def get_node_value(self, name):
        try:
            return self.data.getElementsByTagName(name)[0].childNodes[0].nodeValue
        except IndexError:
            return None

    def get_data(self, raw=False):
        if raw:
            return self.data.toprettyxml()
        else:
            return self.data


class EstaffConnector(object):
    def __init__(self,
                 service_name,
                 api_base_url=estaff_api_base_url,
                 estaff_username=estaff_username,
                 estaff_password=estaff_password,
                 ):
        self.service_name = service_name
        self.api_base_url = api_base_url
        self.estaff_username = estaff_username
        self.estaff_password = estaff_password
        self.params = []
        self.soapaction = None

    def _base_request_object(self, raw=False):

        root = ET.Element('x:Envelope')
        root.set('xmlns:x', 'http://schemas.xmlsoap.org/soap/envelope/')
        root.set('xmlns:www', 'http://www.estaff365.com')
        header = ET.SubElement(root, "x:Header")
        security = ET.SubElement(header, 'wsse:Security')
        security.set('xmlns:wsse', 'http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd')
        security.set('xmlns:wsu', 'http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-utility-1.0.xsd')
        auth = ET.SubElement(security, 'wsse:UsernameToken')
        uname = ET.SubElement(auth, 'wsse:Username')
        uname.text = self.estaff_username
        upass = ET.SubElement(auth, 'wsse:Password')
        upass.text = self.estaff_password
        upass.set('Type',
                  'http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-username-token-profile-1.0#PasswordText')
        body = ET.SubElement(root, "x:Body")
        if self.soapaction:
            action = ET.SubElement(body, "www:{soapaction}".format(soapaction=self.soapaction))
            if self.params:
                for param in self.params:
                    myparam = ET.SubElement(action, "www:{paramname}".format(paramname=param))
                    myparam.text = self.params[param]

        if raw:
            return minidom.parseString(ET.tostring(root)).toprettyxml()
        else:
            return root

    def _base_header_object(self, raw=False):

        headers = {
            'content-type': "text/xml; charset=utf-8",
            'authorization': "Basic"
        }
        if self.soapaction:
            headers['soapaction'] = '{baseurl}I{service_name}/{soapaction}'.format(
                service_name=self.service_name,
                baseurl=estaff_base_url,
                soapaction=self.soapaction
            )

        return headers

    def _base_url(self):
        url = '{baseurl}{service_name}.svc/basic'.format(
            service_name=self.service_name,
            baseurl=estaff_api_base_url,
        )
        return url

    def _build_request_object(self):
        base_obj = self._base_request_object()

    def request_object(self):
        return self._base_request_object(raw=True)

    def set_soapaction(self, soapaction):
        self.soapaction = soapaction

    def set_params(self, params):
        self.params = params

    def send_request(self):
        url = self._base_url()
        payload = self.request_object()
        headers = self._base_header_object()
        response = requests.request("POST", url, data=payload, headers=headers)
        return minidom.parseString(response.text)


class EstaffOnboarding(xmlHelper):

    def __init__(self, data):
        self.data = data

    def unique_id(self):
        return self.get_node_value('UniqueId')

    def employee(self, candidate_id=None):
        return get_employee(unique_id=self.unique_id(), candidate_id=candidate_id)

    def onboarding_state(self):
        return self.get_node_value('OnboardingState')

    def is_application_complete(self):
        if self.get_node_value('IsApplicationComplete') == 'true':
            return True
        else:
            return False

    def is_onboarding_complete(self):
        if self.onboarding_state() == 'Completed':
            return True
        else:
            return False

    def is_complete(self):
        if self.is_onboarding_complete() and self.is_application_complete():
            return True
        else:
            return False


class EstaffCandidate(xmlHelper):

    def __init__(self, unique_id, data, candidate_id=None):
        self.unique_id = unique_id
        self.data = data.getElementsByTagName('GetEmployeeResult')[0]
        self.full_name = '{first_name} {last_name}'.format(
            first_name=self.get_node_value('FirstName'),
            last_name=self.get_node_value('LastName')
        )
        if not candidate_id:
            self.candidate_id = self.get_node_value('EmployeeKey')
        else:
            self.candidate_id = candidate_id

    def get_data(self, raw=False):
        if raw:
            return self.data.toprettyxml()
        else:
            return self.data

    def get_er_candidate(self):
        return Candidate(self.candidate_id)

    def has_references(self):
        if self.count_references() > 0:
            return True
        else:
            return False

    def count_references(self):
        return len(self.list_references())

    def list_references(self):
        return [EstaffReference(x) for x in self.data.getElementsByTagName('Reference')]

    def export_references_to_erecruit(self):
        if self.has_references():
            out = []
            for ref in self.list_references():
                candidate = Candidate(self.candidate_id)
                result = (Candidate(self.candidate_id).add_contact_reference(
                    first_name=ref.first_name(),
                    last_name=ref.last_name(),
                    company_name=ref.company,
                    email=ref.email_address,
                    phone=ref.phone,
                    title=ref.title,
                    reference_text='Relationship to Candidate: ' + ref.relationship + '\n\nQuestions:\n' + reference_note_boilerplate()
                ))
                note = candidate.add_note(
                    'Imported Reference from eStaff ({ref_name}) via WebAPI'.format(ref_name=ref.name), action_id='327')
                out.append(result)
            return out
        else:
            return None


class EstaffReference(xmlHelper):

    def __init__(self, data):
        self.data = data
        self.company = self.get_node_value('Company')
        self.email_address = self.get_node_value('EmailAddress')
        self.name = self.get_node_value('Name')
        self.phone = self.get_node_value('Phone')
        self.relationship = self.get_node_value('Relationship')
        self.title = self.get_node_value('Title')
        self.unique_id = self.get_node_value('UniqueId')

    def get_data(self, raw=False):
        if raw:
            return self.data.toprettyxml()
        else:
            return self.data

    def first_name(self):
        try:
            return str(self.name).split(' ')[0]
        except:
            return self.name

    def last_name(self):
        try:
            names = str(self.name).split(' ')
            names.pop(0)
            return ' '.join(names)
        except:
            return self.name


def get_onboardings_by_date(date, raw=False):
    connect = EstaffConnector(service_name='OnboardingService')
    connect.set_soapaction('GetOnboardingsByDate')
    connect.set_params({'asOfDate': date})
    doc = connect.send_request()
    if raw:
        return doc.toprettyxml()
    else:
        return [EstaffOnboarding(data) for data in doc.getElementsByTagName('Onboarding')]


def get_employee(unique_id, candidate_id=None):
    connect = EstaffConnector(service_name='OnboardingService')
    connect.set_soapaction('GetEmployee')
    connect.set_params({'uniqueId': unique_id})
    doc = connect.send_request()
    return EstaffCandidate(unique_id, data=doc, candidate_id=candidate_id)


def get_completed_onboardings_by_date(date):
    return [onboarding for onboarding in (get_onboardings_by_date(date=date)) if
            onboarding.is_complete() and onboarding.employee().has_references()]


def export_references_to_erecruit_by_date(date=None, grouped=False):
    if not date:
        date = datetime.strftime(datetime.today() - timedelta(days=1), '%Y-%m-%dT%H:%M:%S')
    onboardings = get_completed_onboardings_by_date(date)

    references_grouped = [x.employee().export_references_to_erecruit() for x in onboardings]
    out = []
    for x in references_grouped:
        if grouped:
            out.append([x[0].candidate, x])
        else:
            for reference in x:
                out.append(reference)
    return out


def export_references_to_erecruit_previous_24_hrs():
    return export_references_to_erecruit_by_date()


def getNodeText(node):
    nodelist = node.childNodes
    result = []
    for node in nodelist:
        if node.nodeType == node.TEXT_NODE:
            result.append(node.data)
    return ''.join(result)
