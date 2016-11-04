
import argparse
import filecmp
import json
import tempfile

from googleapiclient import discovery
from googleapiclient import http

from oauth2client.client import GoogleCredentials

def create_service():
    credentials = GoogleCredentials.get_application_default()
    return discovery.build('storage', 'v1', credentials=credentials)

def upload_object(bucket, filename, readers, owners):
    service = create_service()

    # This is the request body as specified:
    # http://g.co/cloud/storage/docs/json_api/v1/objects/insert#request
    body = {
        'name': filename,
    }

    # If specified, create the access control objects and add them to the
    # request body
    if readers or owners:
        body['acl'] = []

    for r in readers:
        body['acl'].append({
            'entity': 'user-%s' % r,
            'role': 'READER',
            'email': r
        })
    for o in owners:
        body['acl'].append({
            'entity': 'user-%s' % o,
            'role': 'OWNER',
            'email': o
        })

    # Now insert them into the specified bucket as a media insertion.
    # http://g.co/dv/resources/api-libraries/documentation/storage/v1/python/latest/storage_v1.objects.html#insert
    with open(filename, 'rb') as f:
        req = service.objects().insert(
            bucket=bucket, body=body,
            # You can also just set media_body=filename, but for the sake of
            # demonstration, pass in the more generic file handle, which could
            # very well be a StringIO or similar.
            media_body=http.MediaIoBaseUpload(f, 'application/octet-stream'))
        resp = req.execute()

    return resp



def get_object(bucket, filename, out_file):
    service = create_service()

    # Use get_media instead of get to get the actual contents of the object.
    # http://g.co/dv/resources/api-libraries/documentation/storage/v1/python/latest/storage_v1.objects.html#get_media
    req = service.objects().get_media(bucket=bucket, object=filename)

    downloader = http.MediaIoBaseDownload(out_file, req)

    done = False
    while done is False:
        status, done = downloader.next_chunk()
        print("Download {}%.".format(int(status.progress() * 100)))

    return out_file

def main(bucket, filename, readers=[], owners=[]):
    print('Uploading object..')
    resp = upload_object(bucket, filename, readers, owners)
    print(json.dumps(resp, indent=2))

    print('Fetching object..')
    with tempfile.NamedTemporaryFile(mode='w+b') as tmpfile:
        get_object(bucket, filename, out_file=tmpfile)
        tmpfile.seek(0)

        if not filecmp.cmp(filename, tmpfile.name):
            raise Exception('Downloaded file != uploaded object')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('filename', help='The name of the file to upload')
    parser.add_argument('bucket', help='Your Cloud Storage bucket.')
    parser.add_argument('--reader', action='append', default=[],
                        help='Your Cloud Storage bucket.')
    parser.add_argument('--owner', action='append', default=[],
                        help='Your Cloud Storage bucket.')

    args = parser.parse_args()

    main(args.bucket, args.filename, args.reader, args.owner)