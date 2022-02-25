import json
import os

import boto3
from plumbum import local

from exporter.domain import Rfc1808Url, DriftOutput


class DriftScanCmdException(Exception):
    ...


class DriftScanCmdRepository:
    def __init__(self):
        self.driftctl = local["driftctl"]

    def scan(self):
        scan_result = None
        try:
            scan_result = self.driftctl("scan", "-o", "json://stdout", "--quiet", retcode=None)

            result_in_json = json.loads(scan_result)

            DriftOutput.from_json(result_in_json)
        except json.JSONDecodeError as ctx:
            raise DriftScanCmdException(
                f"""The drift scan didn't complete successfully. Command output:
                python_error: {str(ctx)}
                cmd_output: {scan_result} 
                """)

        return scan_result


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
