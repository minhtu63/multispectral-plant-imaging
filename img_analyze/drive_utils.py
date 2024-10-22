from googleapiclient.discovery import build
from google.oauth2 import service_account
from googleapiclient.http import MediaFileUpload
import os
import zipfile
import datetime
import sys
sys.path.append('/home/tu/.local/lib/python3.6/site-packages')
sys.path.append('/usr/local/lib/python3.6/dist-packages')
sys.path.append('/usr/lib/python3/dist-packages')
sys.path.append('/usr/lib/python3.6/dist-packages')
class DriveUtils:
    SCOPES = ["https://www.googleapis.com/auth/drive"]
    SERVICE_ACCOUNT_FILE = '/home/tu/Documents/Thesis/src/img_analyze/automated-418309-295a35f2641e.json'
    PARENT_FOLDER_ID = "1360ZEyCL4i1rJcQSdxejNetIqfeVWO7x"

    def authenticate(self):
        creds = service_account.Credentials.from_service_account_file(self.SERVICE_ACCOUNT_FILE, scopes=self.SCOPES)
        return creds

    def compress_folder(self, folder_path, zip_path):
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(folder_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    zip_info = zipfile.ZipInfo(os.path.relpath(file_path, folder_path))

                    date_time = datetime.datetime(1980, 1, 1, 0, 0, 0)
                    zip_info.date_time = date_time.timetuple()[:6]

                    with open(file_path, 'rb') as file_data:
                        zipf.writestr(zip_info, file_data.read())

    def upload_zip_file(self, zip_path):
        creds = self.authenticate()
        service = build('drive', 'v3', credentials=creds)

        # Correctly capture the name of the zip file including the extension
        file_metadata = {
            'name': os.path.basename(zip_path),  # Ensure the zip file's name is captured correctly
            'parents': [self.PARENT_FOLDER_ID],
            'mimeType': 'application/zip'
        }

        media_body = MediaFileUpload(zip_path, mimetype='application/zip', resumable=True)
        request = service.files().create(body=file_metadata, media_body=media_body)

        response = None
        while response is None:
            try:
                status, response = request.next_chunk()
                if status:
                    print(f"Uploaded {int(status.progress() * 100)}%.")
            except Exception as e:
                print("An error occurred during upload:", e)
                return None
                    
        print("Upload Complete")
        return response

    def upload_folder(self, folder_path):
        # Get the correct name for the zip file
        zip_name = os.path.basename(os.path.normpath(folder_path)) + '.zip'
        zip_path = os.path.join(os.path.dirname(folder_path), zip_name)
        
        # Compress the folder
        self.compress_folder(folder_path, zip_path)

        # Upload the zip file
        self.upload_zip_file(zip_path)

        # Delete the temporary zip file
        os.remove(zip_path)
