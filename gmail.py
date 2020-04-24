import base64
import os
import pickle
from email.mime.text import MIMEText
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

from apiclient import errors


class Gmail:
    """Gmail handles interaction with Gmail API

    Properties:
        CREDENTIALS_FILE -- Client configuration file downloaded after enabling Gmail API
        TOKEN_FILE_NAME  -- The file token.pickle stores the user's access and refresh tokens,
                            and is created automatically when the authorization flow completes
                            for the first time.
    """

    service = None
    CREDENTIALS_FILE = 'credentials.json'
    TOKEN_FILE_NAME = 'token.pickle'
    SCOPES = ['https://www.googleapis.com/auth/gmail.send']

    def __init__(self, *args, **kwargs):
        self.service = self.get_service()
    
    def get_service(self):
        """Generate Gmail service"""
        creds = None
        if os.path.exists(self.TOKEN_FILE_NAME):
            with open(self.TOKEN_FILE_NAME, 'rb') as token:
                creds = pickle.load(token)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.CREDENTIALS_FILE, self.SCOPES)
                creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
            with open(self.TOKEN_FILE_NAME, 'wb') as token:
                pickle.dump(creds, token)
        service = build('gmail', 'v1', credentials=creds)
        return service

    def create_message(self, sender, to, subject, message_text, _subtype='plain'):
        """Create a message for an email.

        Args:
            sender: Email address of the sender.
            to: Email address of the receiver.
            subject: The subject of the email message.
            message_text: The text of the email message.

        Returns:
            An object containing a base64url encoded email object.
        """
        message = MIMEText(message_text, _subtype, 'utf-8')
        message['to'] = to
        message['from'] = sender
        message['subject'] = subject
        return {'raw': base64.urlsafe_b64encode(message.as_bytes ()).decode()}

    def send_message(self, user_id, message):
        """Send an email message.

        Args:
            user_id: User's email address. The special value "me"
            can be used to indicate the authenticated user.
            message: Message to be sent.

        Returns:
            Sent Message.
        """
        try:
            message = (self.service.users().messages().send(userId=user_id, body=message)
                    .execute())
            print('Message Id: %s' % message['id'])
            return message
        except errors.HttpError as error:
            print('An error occurred: %s' % error)


def send_message(sender, to, subject, message, _subtype='plain'):
    gmail = Gmail()
    if type(to) is list:
        to = str(','.join(to))
    email_message = gmail.create_message(sender, to, subject, message, _subtype)
    return gmail.send_message('me', email_message)
