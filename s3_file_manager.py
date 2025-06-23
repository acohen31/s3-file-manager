import os

import tkinter as tk
from tkinter import filedialog
import boto3
from dotenv import load_dotenv
import logging
from botocore.exceptions import ClientError

from progress_monitor import ProgressMonitor

load_dotenv()

class S3FileManager:
    def __init__(self, bucket_name):
        self.s3_client = boto3.client('s3')
        self.bucket_name = bucket_name

    def upload_file(self, filename, object_name=None):
        if object_name is None:
            object_name = os.path.basename(filename)

        try:
            response = self.s3_client.upload_file(filename, self.bucket_name, object_name,
                                                  Callback=ProgressMonitor(filename))
            print(f"Uploaded {filename} to {self.bucket_name}")
        except ClientError as e:
            logging.error(e)
            return False
        return True

    def download_file(self, filename):
        try:
            response = self.s3_client.download_file(Bucket=self.bucket_name, Key=filename, Filename=filename)
            print(f"Downloaded {filename} from {self.bucket_name}")
        except ClientError as e:
            logging.error(e)
            return False
        return True

    def list_files(self, prefix=''):
        try:
            response = self.s3_client.list_objects(Bucket=self.bucket_name, Prefix=prefix)
            print(f'Found {len(response['Contents'])} objects in {self.bucket_name}')
            for obj in response['Contents']:
                print(obj['Key'])
        except ClientError as e:
            logging.error(e)

    def delete_file(self, filename):
        try:
            response = self.s3_client.delete_object(Bucket=self.bucket_name, Key=filename)
            print(f'Deleted {filename} from {self.bucket_name}')
            return True
        except ClientError as e:
            logging.error(e)
            return False

    def copy_to_bucket(self, source):
        try:
            response = self.s3_client.copy_object(Bucket=self.bucket_name, CopySource=source, Key=os.path.basename(source))
            print(response)
            return True
        except ClientError as e:
            logging.error(e)
            return False

    def test_connection(self):
        # Test S3 connection by listing buckets
        try:
            response = self.s3_client.list_buckets()
            # print(f'Successfully connected to S3')
            # for bucket in response['Buckets']:
            #     print(f'    - {bucket["Name"]}')
            return True
        except ClientError as e:
            logging.error(e)
            return False

    def validate_bucket_access(self):
        try:
            self.s3_client.head_bucket(Bucket=self.bucket_name)
            print(f'Successfully accessed bucket {self.bucket_name}')
            return True
        except ClientError as e:
            logging.error(e)

def get_file():
    root = tk.Tk()
    root.withdraw()
    filename = filedialog.askopenfilename(
        initialdir="/",
        title="Select a file",
        filetypes=(("text files", "*.txt"), ("all files", "*.*"))
    )

    if filename:
        return filename

    return None


if __name__ == '__main__':
    manager = S3FileManager(os.getenv('S3_BUCKET_NAME'))
    if not manager.test_connection():
        exit(1)
    # manager.validate_bucket_access()
    # manager.upload_file(get_file(), manager.bucket_name)
    # manager.download_file(input("[Download] Enter file name for download: "))
    # manager.list_files()
    # manager.delete_file(input("[Delete] Enter filename for: "))
    manager.list_files()
    manager.copy_to_bucket(os.getenv('BUCKET2'))
    manager.list_files()
