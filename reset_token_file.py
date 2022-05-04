import argparse
import json
import os
import subprocess

from google.cloud import storage
from google.oauth2 import service_account

parser = argparse.ArgumentParser()
parser.add_argument('--path', default='/tmp/token.json')

service_account_info = json.load(open('cloud_storage_credentials.json'))
credentials = service_account.Credentials.from_service_account_info(service_account_info)
client = storage.Client(
    credentials=credentials,
    project=credentials.project_id,
)

if __name__ == "__main__":
    args = parser.parse_args()
    print('local remove file path={}'.format(args.path))
    os.remove(args.path)

    bucket = client.bucket('sagawa-notice-line-bot')
    blob = bucket.blob('token.json')
    print('cloud storage remove file path=/{}/{}'.format(bucket, blob))
    blob.delete()

    subprocess.call('python main.py', shell=True)
