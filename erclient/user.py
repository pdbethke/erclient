# Functions that can't be duplicated using API 2.0. Hopefully some day...

from .candidate import validate_rest, lookup_rest

def validate(username, password):
   return validate_rest(username, password)

def lookup(email):
   return lookup_rest(email)