# from linebot import LineBotApi
# from linebot.models import TextSendMessage
# from linebot.exceptions import LineBotApiError
# from settings import *
import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']


def push_notice(event, context):
    """Shows basic usage of the Gmail API.
    Lists the user's Gmail labels.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    try:
        # Call the Gmail API
        service = build('gmail', 'v1', credentials=creds)
        now = (datetime.now(timezone(timedelta(hours=+9), 'JST')) + timedelta(minutes=-30)).strftime('%Y/%m/%d')
        messages_data = service.users().messages().list(userId='me', q='from:info@ds.sagawa-exp.co.jp after:{}'.format(now)).execute()
        print(messages_data)

        if not labels:
            print('No labels found.')
            return
        print('Labels:')
        for label in labels:
            print(label['name'])

    except HttpError as error:
        # TODO(developer) - Handle errors from gmail API.
        print(f'An error occurred: {error}')

    # line_bot_api = LineBotApi(CHANNEL_ACCESS_TOKEN)
    # try:
    #     line_bot_api.push_message(USER_ID, TextSendMessage(text=post_data))
    # except LineBotApiError as e:
    #     print(e)
    return "line"


if __name__ == '__main__':
    push_notice('event', 'context')
