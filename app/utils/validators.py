""" Custom validators """

import requests


def validate_response(response):
    if not response.status_code == requests.codes.ok:
        raise requests.HTTPError


def validate_json(response_json):
    if not isinstance(response_json, dict):
        raise TypeError

