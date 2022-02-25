import json
import os

import boto3
from exporter.domain import Rfc1808Url
from plumbum import local


class DriftScanCmdRepository:
    def __init__(self):
        self.driftctl = local["driftctl"]

    def scan(self):
        return self.driftctl("scan", "-o", "json://stdout", "--quiet", retcode=None)


class S3Repository:
    def __init__(self):
        self.s3_session_config = {}
        self._set_custom_config_for_s3_session_if_available()

        self.s3 = boto3.client('s3', **self.s3_session_config)

    def _set_custom_config_for_s3_session_if_available(self):
        s3_endpoint_url = os.getenv('AWS_S3_ENDPOINT_URL')
        s3_access_key_id = os.getenv('AWS_S3_ACCESS_KEY_ID')
        s3_secret_access_key = os.getenv('AWS_S3_SECRET_ACCESS_KEY')

        if s3_endpoint_url and all([s3_access_key_id, s3_secret_access_key]):
            self.s3_session_config.update(
                {'endpoint_url': os.getenv('AWS_S3_ENDPOINT_URL'),
                 'aws_access_key_id': os.getenv('AWS_S3_ACCESS_KEY_ID'),
                 'aws_secret_access_key': os.getenv('AWS_S3_SECRET_ACCESS_KEY')
                 })

    def save(self, output_config, content):
        self.s3.put_object(Key=output_config.path, Bucket=output_config.netloc, Body=content,
                           ContentType="application/json")

    def open(self, url: Rfc1808Url):
        result = self.s3.get_object(Key=url.path, Bucket=url.netloc)

        return json.load(result.get('Body'))
