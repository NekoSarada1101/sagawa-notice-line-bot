import base64
import json
import os
from datetime import datetime, timedelta, timezone

from google.auth.transport.requests import Request
from google.cloud import storage
from google.cloud import secretmanager
from google.oauth2.credentials import Credentials
from google.api_core.exceptions import NotFound
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from linebot import LineBotApi
from linebot.exceptions import LineBotApiError
from linebot.models import TextSendMessage


storage_client = storage.Client()
secret_client = secretmanager.SecretManagerServiceClient()

CHANNEL_ACCESS_TOKEN = secret_client.access_secret_version(request={'name': 'projects/slackbot-288310/secrets/SAGAWA_NOTICE_LINE_CHANNEL_ACCESS_TOKEN/versions/1'})
USER_ID = secret_client.access_secret_version(request={'name': 'projects/slackbot-288310/secrets/LINE_USER_ID/versions/1'})
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']


def push_notice(event, context):
    """Shows basic usage of the Gmail API.
    Lists the user's Gmail labels.
    """
    try:
        bucket = storage_client.get_bucket('sagawa-notice-line-bot')
        blob = bucket.blob('token.json')
        blob.download_to_filename("/tmp/token.json")
    except NotFound as error:
        print(error)

    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('/tmp/token.json'):
        creds = Credentials.from_authorized_user_file('/tmp/token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('gmail_api_credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('/tmp/token.json', 'w') as token:
            token.write(creds.to_json())
        blob.upload_from_filename('/tmp/token.json')

    try:
        # 実行時から30分前の佐川配達通知メールを取得する
        service = build('gmail', 'v1', credentials=creds)
        now = (datetime.now(timezone(timedelta(hours=+9), 'JST')) + timedelta(minutes=-30)).strftime('%Y/%m/%d')
        messages_data = service.users().messages().list(userId='me', q='from:info@ds.sagawa-exp.co.jp after:{}'.format(now)).execute()
        print(messages_data)

        if messages_data['resultSizeEstimate'] == 0:
            print('No Data')
            return

        # メールの本文を取得する
        for message_id in messages_data['messages']:
            detail = service.users().messages().get(userId='me', id=message_id['id']).execute()
            decoded_bytes = base64.urlsafe_b64decode(detail["payload"]["body"]["data"])
            decoded_message = decoded_bytes.decode("UTF-8")

            # メール本文を整形する
            decoded_message = decoded_message.replace('　', '')
            decoded_message_arr = decoded_message.split('\r\n')
            notice_message = ''
            for index, message_row in enumerate(decoded_message_arr):
                if 5 <= index <= 16:
                    notice_message += message_row + '\n'

            # LINEに通知
            line_bot_api = LineBotApi(CHANNEL_ACCESS_TOKEN)
            try:
                line_bot_api.push_message(USER_ID, TextSendMessage(text=notice_message))
            except LineBotApiError as e:
                print(e)

    except HttpError as error:
        # TODO(developer) - Handle errors from gmail API.
        print(f'An error occurred: {error}')


if __name__ == '__main__':
    push_notice('event', 'context')
