#!/usr/bin/python
# -*- coding: latin-1 -*-

import os

client_id = os.environ.get('ER_CLIENT_ID', None)
client_secret = os.environ.get('ER_CLIENT_SECRET', None)

rest_username = os.environ.get('ER_REST_USERNAME', None)
rest_password = os.environ.get('ER_REST_PASSWORD', None)
rest_entity_id = os.environ.get('ER_REST_ENTITY_ID', None)

estaff_username = os.environ.get('ER_ESTAFF_USERNAME', None)
estaff_password = os.environ.get('ER_ESTAFF_PASSWORD', None)
estaff_base_url = os.environ.get('ER_ESTAFF_BASE_URL', None)
estaff_api_base_url = os.environ.get('ER_ESTAFF_API_BASE_URL', None)

if os.environ.get('ER_TOKEN_URL', None):
    token_url = os.environ.get('ER_TOKEN_URL')
else:
    token_url = None
if os.environ.get('ER_BASE_URL', None):
    api_base_url = os.environ.get('ER_BASE_URL') + 'WebAPI/'
    api_base_url_rest = os.environ.get('ER_BASE_URL') + 'RestServices/'
else:
    api_base_url = None
    api_base_url_rest = None


schema_dir = 'schema/'

note_schema = {
    "Records": [
        {
            "Type": "NOTHING",
            "ID": 0
        }
    ],
    "NoteBody": "string",
    "NoteActionID": 0
}

attachment_type_schema = [{'ID': 1, 'Name': 'Resumé', 'ApplicableTo': [6, 90]},
                          {'ID': 2, 'Name': 'Agreement', 'ApplicableTo': [5, 13, 1]},
                          {'ID': 4, 'Name': 'Invoice', 'ApplicableTo': [17]},
                          {'ID': 5, 'Name': 'Employment Letter', 'ApplicableTo': [6]},
                          {'ID': 6, 'Name': 'Letter of Recommendation', 'ApplicableTo': [6]},
                          {'ID': 7, 'Name': 'Medical', 'ApplicableTo': [6]},
                          {'ID': 8, 'Name': 'Onboarding Documents', 'ApplicableTo': [6]},
                          {'ID': 10, 'Name': 'Signed Forms & Agreements', 'ApplicableTo': [6, 7]},
                          {'ID': 12, 'Name': "Worker's Comp Claims", 'ApplicableTo': [6]},
                          {'ID': 13, 'Name': 'Scanned IDs', 'ApplicableTo': [6]},
                          {'ID': 15, 'Name': 'Miscellaneous', 'ApplicableTo': [6]},
                          {'ID': 16, 'Name': 'Miscellaneous', 'ApplicableTo': [13, 6, 1, 2, 50, 5, 80, 3, 4]},
                          {'ID': 19, 'Name': 'Assessments', 'ApplicableTo': [6]},
                          {'ID': 29, 'Name': 'Cand. Work Samples(Caution-Cand. sees these)', 'ApplicableTo': [6, 5]},
                          {'ID': 33, 'Name': 'Employment Agreements', 'ApplicableTo': [5]},
                          {'ID': 38, 'Name': 'Recruiter Attachment', 'ApplicableTo': [7]},
                          {'ID': 39, 'Name': 'Vendor - Certificate of Liability', 'ApplicableTo': [6, 1]},
                          {'ID': 40, 'Name': 'Vendor - Supplier Provider Agreement', 'ApplicableTo': [6, 1]},
                          {'ID': 41, 'Name': 'Vendor - W9', 'ApplicableTo': [6, 1]},
                          {'ID': 201, 'Name': 'Invoice PDF', 'ApplicableTo': []}, {'ID': 1000, 'Name': 'Other',
                                                                                   'ApplicableTo': [6, 2, 1, 5, 13, 12,
                                                                                                    4, 7, 50, 90, 53,
                                                                                                    54, 220, 290]},
                          {'ID': 1002, 'Name': 'Application', 'ApplicableTo': [6]},
                          {'ID': 1003, 'Name': 'IC Assessment', 'ApplicableTo': [13, 6]},
                          {'ID': 1004, 'Name': 'IC Acknowledgement', 'ApplicableTo': [13, 6]},
                          {'ID': 1005, 'Name': 'Certificate of Good Standing', 'ApplicableTo': [13, 6]},
                          {'ID': 1006, 'Name': 'Certificate of Insurance', 'ApplicableTo': [13, 6, 1]},
                          {'ID': 1008, 'Name': 'Consultant Project Agreement', 'ApplicableTo': [13, 6, 5]},
                          {'ID': 1009, 'Name': 'Candidate Portfolio Samples', 'ApplicableTo': [6, 5]},
                          {'ID': 1010, 'Name': 'Candidate Bio', 'ApplicableTo': [6]},
                          {'ID': 1011, 'Name': 'Rate Card', 'ApplicableTo': [13, 6, 1, 2, 5, 4]},
                          {'ID': 1012, 'Name': 'Subcontractor Onboarding Checklist', 'ApplicableTo': [6]},
                          {'ID': 1013, 'Name': 'References (Caution- Cand. sees these attachments)',
                           'ApplicableTo': [6]}, {'ID': 1014, 'Name': 'Background Check', 'ApplicableTo': [6]},
                          {'ID': 1016, 'Name': 'Benefits', 'ApplicableTo': [6]},
                          {'ID': 1017, 'Name': 'Disciplinary ', 'ApplicableTo': [6]},
                          {'ID': 1018, 'Name': 'Drug Screen', 'ApplicableTo': [6]},
                          {'ID': 1019, 'Name': 'Background/Drug Certification Form', 'ApplicableTo': [13, 6, 5]},
                          {'ID': 1020, 'Name': 'Client Data Privacy & Security', 'ApplicableTo': [13, 6, 5]},
                          {'ID': 1021, 'Name': 'Client Benefits Waiver', 'ApplicableTo': [13, 6, 5]},
                          {'ID': 1022, 'Name': 'Client HIPPA Form', 'ApplicableTo': [13, 6, 5]},
                          {'ID': 1023, 'Name': 'Client Policy/Code of Ethics Form', 'ApplicableTo': [13, 6, 5]},
                          {'ID': 1024, 'Name': 'Client Conflict Of Interest Form', 'ApplicableTo': [13, 6, 5]},
                          {'ID': 1025, 'Name': 'Client IP/Work Product Release', 'ApplicableTo': [13, 6, 5]},
                          {'ID': 1026, 'Name': 'Candidate Agreement - Temp', 'ApplicableTo': [6]},
                          {'ID': 1027, 'Name': 'Candidate Agreement - Perm', 'ApplicableTo': [6]},
                          {'ID': 1028, 'Name': 'Candidate Agreement - Consulting', 'ApplicableTo': [6]},
                          {'ID': 1029, 'Name': 'Candidate Policies/Acknowledgement', 'ApplicableTo': [6]},
                          {'ID': 1030, 'Name': 'Candidate Data Privacy/Security', 'ApplicableTo': [6]},
                          {'ID': 1031, 'Name': 'Candidate Offsite Agreement', 'ApplicableTo': [13, 6, 5]},
                          {'ID': 1032, 'Name': 'Candidate Travel Agreement', 'ApplicableTo': [13, 6, 5]},
                          {'ID': 1033, 'Name': 'Candidate Equipment Release', 'ApplicableTo': [13, 6, 5]},
                          {'ID': 1034, 'Name': 'Virtual Employee Policy Acknowledgement', 'ApplicableTo': [13, 6, 5]},
                          {'ID': 1035, 'Name': 'Model Release', 'ApplicableTo': [13, 6, 1, 2, 5, 4]},
                          {'ID': 1036, 'Name': 'Medical', 'ApplicableTo': [6]},
                          {'ID': 1037, 'Name': 'Performance Related ', 'ApplicableTo': [6]},
                          {'ID': 1038, 'Name': 'I-9', 'ApplicableTo': [6]},
                          {'ID': 1039, 'Name': 'W-4', 'ApplicableTo': [6]},
                          {'ID': 1040, 'Name': 'W9', 'ApplicableTo': [13, 6, 1, 2, 5, 4]},
                          {'ID': 1041, 'Name': "Scanned ID's (e-Verify)", 'ApplicableTo': [6]},
                          {'ID': 1042, 'Name': 'State Tax Forms', 'ApplicableTo': [6]},
                          {'ID': 1043, 'Name': 'Local Tax Forms', 'ApplicableTo': [6]},
                          {'ID': 1044, 'Name': 'Direct Deposit Form', 'ApplicableTo': [6]},
                          {'ID': 1045, 'Name': 'Tax Exempt Certificate', 'ApplicableTo': [13, 1, 2]},
                          {'ID': 1046, 'Name': 'Workers Comp Claims', 'ApplicableTo': [6]},
                          {'ID': 1047, 'Name': 'Credit Reports', 'ApplicableTo': [1]},
                          {'ID': 1048, 'Name': 'Client Based - Master', 'ApplicableTo': [13, 1, 2]},
                          {'ID': 1049, 'Name': 'Client Based - Temp', 'ApplicableTo': [13, 1, 2]},
                          {'ID': 1050, 'Name': 'Client Based - Perm', 'ApplicableTo': [13, 1, 2]},
                          {'ID': 1051, 'Name': 'Temp Svc Agreement', 'ApplicableTo': [13, 1, 2]},
                          {'ID': 1052, 'Name': 'Direct Hire Agreement', 'ApplicableTo': [13, 1, 2]},
                          {'ID': 1053, 'Name': 'Client Offsite Agreement', 'ApplicableTo': [13, 1, 2, 5, 4]},
                          {'ID': 1054, 'Name': 'Client Travel Agreement', 'ApplicableTo': [13, 1, 2, 4]},
                          {'ID': 1055, 'Name': 'Non-Disclosure Agreement', 'ApplicableTo': [13, 6, 1, 2, 5, 4]},
                          {'ID': 1056, 'Name': 'RFPs/Proposals', 'ApplicableTo': [13, 1, 3]},
                          {'ID': 1057, 'Name': 'Statement of Work', 'ApplicableTo': [13, 6, 1, 2, 5, 4]},
                          {'ID': 1058, 'Name': 'Purchase Order', 'ApplicableTo': [13, 21, 1, 2, 5, 4]},
                          {'ID': 1059, 'Name': 'Work Order', 'ApplicableTo': [13, 6, 1, 2, 5, 4]},
                          {'ID': 1060, 'Name': 'Task Order', 'ApplicableTo': [13, 1, 2, 5, 4]},
                          {'ID': 1061, 'Name': 'Agrmt. Amd', 'ApplicableTo': [13, 6, 1, 2, 5, 4]},
                          {'ID': 1062, 'Name': 'Agrmt. Addendum ', 'ApplicableTo': [13, 6, 1, 2, 5, 4]},
                          {'ID': 1063, 'Name': 'Quality Reviews/Surveys', 'ApplicableTo': [5]},
                          {'ID': 1064, 'Name': 'Audits & Reports', 'ApplicableTo': [13, 1, 2, 5, 4]},
                          {'ID': 1065, 'Name': 'Correspondence', 'ApplicableTo': [13, 6, 1, 2, 5, 4]},
                          {'ID': 1066, 'Name': 'Reps & Certs', 'ApplicableTo': [13, 1]},
                          {'ID': 1067, 'Name': 'Client Equipment Agreement', 'ApplicableTo': [13, 1, 2, 5, 4]},
                          {'ID': 1068, 'Name': 'Disciplinary', 'ApplicableTo': [6]},
                          {'ID': 1069, 'Name': 'Performance Related', 'ApplicableTo': [6]},
                          {'ID': 1070, 'Name': 'Other', 'ApplicableTo': [21]},
                          {'ID': 1071, 'Name': 'Invoicing Instructions', 'ApplicableTo': [21]},
                          {'ID': 1073, 'Name': 'Vendor Agreement ', 'ApplicableTo': [13]},
                          {'ID': 1074, 'Name': 'Referral Form', 'ApplicableTo': [6]},
                          {'ID': 1075, 'Name': 'Scorecard', 'ApplicableTo': [4]}]


def get_attachment_type_id_from_name(name):
    try:
        return (([x for x in attachment_type_schema if name in x['Name']][0])['ID'])
    except:
        return None

def reference_note_boilerplate():
    part1 = [
        'Characterize the length and nature of your relationship with the talent including dates of employment and employee\'s title.',
        'Did the talent work as part of a team? If so - what was the size and overall make up of the team?',
        'What were the 3 key strengths the talent had while working with you?',
        'If the applicant were still working with you, what is one area that you would want to help them grow and see them strengthen?',
        'Specifically, what were the most prevalent areas of learning opportunity for the talent back then?',
        'What would you cite as the talent\'s biggest accomplishment while in the role?',
        'Describe the talent\'s reliability in the office - did they consistently show up to work on time, put in the hours necessary to get the job done and a not take excessive time off?  Also, speak to their reliability from home if they worked from home.',
        'If possible would you rehire the talent as a part of your team again in the future?',
        'Please share any additional comments that may assist in placing this person:',

    ]

    part2 = [

        'Just for my own understanding, tell me a bit about the roles you have played and how would you differentiate your background from this talent?'

    ]

    part3 = [

        'I don\'t want to take this conversation away from the talent, but after hearing about you and your company I am just curious to learn more to see if we can partner together to assist your company in any way.'

    ]

    part4 = [

        'And, of course, I wouldn?t be doing my job if I didn?t put on my sales hat for just a minute (launch into a research question)',
        'So how did you find this talent?',
        'Can you confirm some of the details of the department in which you worked together?',
        'Talent said he/she reported directly to you ? how many additional employees reside within the department?'
    ]

    boilerplate =  [('', part1), ('Lead Generation Candidate', part2), ('Client', part3), ('', part4)]

    out = ''
    for x in boilerplate:
        if x[0]:
            out += (x[0] + ':')
            out += '\n'
        for y in x[1]:
            out += ('- {question}'.format(question=y))
            out += '\n'
        out += '\n'

    return out