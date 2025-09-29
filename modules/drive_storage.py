"""
Google Drive Storage Module
Handles file uploads and storage in Google Drive
"""

from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import os
import tempfile

class DriveStorage:
    def __init__(self, credentials_file='credentials.json', folder_id=None):
        """Initialize Google Drive connection"""
        
        scope = ['https://www.googleapis.com/auth/drive.file']
        self.creds = Credentials.from_service_account_file(credentials_file, scopes=scope)
        self.service = build('drive', 'v3', credentials=self.creds)
        self.folder_id = folder_id
        
        # Create folder if not specified
        if not self.folder_id:
            self.folder_id = self._create_folder('Cleaning_Business_Files')
    
    def _create_folder(self, folder_name):
        """Create a folder in Google Drive"""
        file_metadata = {
            'name': folder_name,
            'mimeType': 'application/vnd.google-apps.folder'
        }
        
        folder = self.service.files().create(
            body=file_metadata,
            fields='id'
        ).execute()
        
        # Make folder publicly accessible
        self.service.permissions().create(
            fileId=folder.get('id'),
            body={'type': 'anyone', 'role': 'reader'}
        ).execute()
        
        return folder.get('id')
    
    def upload_file(self, file_path, file_name=None):
        """Upload file to Google Drive"""
        if not file_name:
            file_name = os.path.basename(file_path)
        
        file_metadata = {
            'name': file_name,
            'parents': [self.folder_id] if self.folder_id else []
        }
        
        media = MediaFileUpload(file_path, resumable=True)
        
        file = self.service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id, webViewLink'
        ).execute()
        
        # Make file publicly accessible
        self.service.permissions().create(
            fileId=file.get('id'),
            body={'type': 'anyone', 'role': 'reader'}
        ).execute()
        
        return f"https://drive.google.com/file/d/{file.get('id')}/view"
    
    def delete_file(self, file_id):
        """Delete file from Google Drive"""
        try:
            self.service.files().delete(fileId=file_id).execute()
            return True
        except:
            return False
    
    def list_files(self):
        """List all files in the folder"""
        query = f"'{self.folder_id}' in parents" if self.folder_id else None
        
        results = self.service.files().list(
            q=query,
            pageSize=100,
            fields="files(id, name, createdTime, size, webViewLink)"
        ).execute()
        
        return results.get('files', [])