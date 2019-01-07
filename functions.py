import os
import re
import json
import string
import random
import logging
import jinja2
import cloudstorage as gcs

from google.appengine.ext import blobstore
from google.appengine.api import images, urlfetch
from google.appengine.api.app_identity import get_default_gcs_bucket_name

BUCKET_NAME = '/' + get_default_gcs_bucket_name() + '/'

def generate_random_string(n=8):
    """Generate random string could be used for IDs, etc"""
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(n))

def json_response(response, callback=None):
    code = response.get("status") or 200

    """Return a JSON string from a Python dictionary"""
    if callback:
        return callback + '(' + json.dumps(response) + ');', code, {'Content-Type': 'application/json'}
    return json.dumps(response), code, {'Content-Type': 'application/json'}

def is_email(email):
    pattern = '^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$'
    return re.match(pattern, email)

def save_to_gcs(file, bucket_name=BUCKET_NAME):
    filename = bucket_name
    filename += generate_random_string(16) + '/'
    filename += file.filename

    gcs_options = {'x-goog-acl': 'public-read'}
    gcs_file = gcs.open(filename, 'w', options=gcs_options)
    gcs_file.write(file.read())
    gcs_file.close()

    file_url = "https://storage.googleapis.com" + filename

    try:
        blob_key = blobstore.create_gs_key("/gs" + filename)
        serving_url = images.get_serving_url(blob_key)
    except Exception as e:
        logging.debug('File is not an image')
        logging.exception(e)
        serving_url = file_url

    return {
        "serving_url": serving_url,
        "blob_key": blob_key
    }
