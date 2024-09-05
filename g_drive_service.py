import os
from googleapiclient.discovery import build
from google.oauth2.service_account import Credentials

class GoogleDriveService:
    def __init__(self):
        self._SCOPES = ['https://www.googleapis.com/auth/drive']
        _base_path = os.path.dirname(__file__)
        _credential_path = os.path.join(_base_path, 'credential.json')
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = _credential_path

    def build(self):
        creds = Credentials.from_service_account_file(os.getenv("GOOGLE_APPLICATION_CREDENTIALS"), scopes=self._SCOPES)
        service = build('drive', 'v3', credentials=creds)
        return service
