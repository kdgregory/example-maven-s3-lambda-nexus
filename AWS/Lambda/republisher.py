# Copyright 2016 Keith D Gregory (www.kdgregory.com)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import print_function

import base64
import boto3
import httplib
import re
import tempfile
import urllib


NEXUS_HOST = '172.30.0.120'
NEXUS_PORT = 8081
NEXUS_BASE_PATH = '/nexus/content/repositories/'
NEXUS_SNAPSHOT_PATH = NEXUS_BASE_PATH + 's3-snapshots/'
NEXUS_RELEASE_PATH = NEXUS_BASE_PATH + 's3-releases/'

AUTH_HEADER = "Basic " + base64.b64encode('deployment:deployment123')


print('Loading function')

s3 = boto3.resource('s3')


def lambda_handler(event, context):

    bucket = event['Records'][0]['s3']['bucket']['name']
    key = urllib.unquote_plus(event['Records'][0]['s3']['object']['key'].encode('utf8'))
    if should_process(key):
        print('processing: ' + key)
        staging_file = tempfile.TemporaryFile()
        try:
            download_to_staging(event, bucket, key, staging_file)
            upload_to_nexus(staging_file, key)
            return True
        except Exception as e:
            print('Error processing ' + key)
            print(e)
            raise e
        finally:
            staging_file.close()
    else:
        print('ignoring:   ' + key)


def should_process(key):
    return (key.startswith('snapshots/') or key.startswith('releases/')) \
       and (not key.endswith('/')) \
       and (key.find('maven-metadata.xml') == -1)


def download_to_staging(event, bucket, key, staging_file):
    s3.Object(bucket, key).download_fileobj(staging_file)
    staging_file.flush()
    print("downloaded {} bytes; reported size in event is {}"
          .format(staging_file.tell(), event['Records'][0]['s3']['object']['size']))


def upload_to_nexus(staging_file, key):
    request_path = get_destination_url(key)
    print("uploading file to: http://{}:{}{}".format(NEXUS_HOST, NEXUS_PORT, request_path))
    cxt = httplib.HTTPConnection(NEXUS_HOST, NEXUS_PORT)
    try:
        staging_file.seek(0)
        cxt.request("PUT", request_path, staging_file, { "Authorization": AUTH_HEADER })
        response = cxt.getresponse()
        print("response status: {}".format(response.status))
    finally:
        cxt.close()


def get_destination_url(key):
    if key.startswith("snapshots/"):
        return NEXUS_SNAPSHOT_PATH + re.sub(r'-\d{8}\.\d{6}-\d+', '-SNAPSHOT', key[10:])
    elif key.startswith("releases/"):
        return NEXUS_RELEASE_PATH + key[9:]
    else:
        raise Exception("invalid key (should not get here): " + key)
