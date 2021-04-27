# erclient
Client for Erecruit V2 API (Json/OAuth) with fallback to REST API

Requires that the following variables be set in the local ENV:

ER_BASE_URL (url, base URL for API 2.0, eg "https://erecruit.example.com/")

ER_TOKEN_URL (url, base Token URL for API 2.0,  eg "https://erecruit.example.com/t/token")

ER_CLIENT_ID (string, Client ID for API 2.0,  eg "ABCD123456")

ER_CLIENT_SECRET (string, Client Password for API 2.0, eg "ABCD123456")

ER_REST_ENTITY_ID (string, the REST 1.0 API Entity ID, eg "00000000-0000-0000-0000-000000000E01")

ER_REST_USERNAME (string, the REST 1.0 API Username eg "webapi@example.com")

ER_REST_PASSWORD (string, the REST 1.0 API Password eg "MyPassword")

The following variables are for eStaff365 integration and are optional:

ER_ESTAFF_API_BASE_URL (string, typically "https://www.estaff365.com:8443/")

ER_ESTAFF_BASE_URL (string, typically "http://www.estaff365.com/")

ER_ESTAFF_PASSWORD (string, eg "MyPassword")

ER_ESTAFF_USERNAME (string, eg "service@Example")

Example Script: (generates a random, fully populated and authenticated candidate record with optional PDF resume parsing):

```
import random, os, time
from faker import Faker

from erclient.address import list_address_states
from erclient.adsource import list_adsources
from erclient.candidate import create_candidate_rest as create_candidate
from erclient.foldergroup import list_foldergroups
from erclient.position import list_posted_positions

fake = Faker()

tic = time.perf_counter()
foldergroup = random.choice(list_foldergroups())
adsource = random.choice(list_adsources(abouttype_id='Candidate'))
state = random.choice(list_address_states())
title = foldergroup.name
fname = fake.first_name()
lname = fake.last_name()
phone = fake.phone_number()
email = fake.ascii_safe_email()
zipcode = fake.postcode()
password = fake.password()
try:
    position = random.choice(list_posted_positions())
    position_id = position.position_id
except IndexError:
    position_id = None
portfolio_url = fake.url()
resume = None
if os.path.exists('resume.pdf'):
    with open('resume.pdf', 'rb') as resume:
        candidate = create_candidate(
            first=fname,
            last=lname,
            folder_group_id=foldergroup.foldergroup_id,
            title=title,
            adsource=adsource,
            email_address=email,
            phone_number=phone,
            address_1=fake.street_address(),
            city=fake.city(),
            state_id=state.address_state_id,
            postal_code=zipcode,
            password=password,
            position_id=position_id,
            portfolio_url=portfolio_url,
            resume=resume
        )
else:
        candidate = create_candidate(
            first=fname,
            last=lname,
            folder_group_id=foldergroup.foldergroup_id,
            title=title,
            adsource=adsource,
            email_address=email,
            phone_number=phone,
            address_1=fake.street_address(),
            city=fake.city(),
            state_id=state.address_state_id,
            postal_code=zipcode,
            password=password,
            position_id=position_id,
            portfolio_url=portfolio_url,
            resume=None
        )
toc = time.perf_counter()
print('Candidate {name}, ID#{id} created in {duration} seconds'.format(name=candidate, id=candidate.candidate_id, duration=toc - tic))
```