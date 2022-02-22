import json
import os
from uuid import uuid4

import pytest

from exporter.domain import Rfc1808Url
from exporter.repositories import S3Repository


@pytest.fixture
def configure_minio_env_vars():
    os.environ['AWS_S3_ENDPOINT_URL'] = 'http://s3:9000'
    os.environ['AWS_S3_ACCESS_KEY_ID'] = 'key'
    os.environ['AWS_S3_SECRET_ACCESS_KEY'] = 'some-secret'


@pytest.fixture
def sample_json_file_url(configure_minio_env_vars):
    url = Rfc1808Url.from_url(f"s3://drift-bucket/{uuid4()}")
    content = {"SomeSampleJsonKey": "SomeSampleJsonValue"}

    S3Repository().save(url, json.dumps(content))

    return url, content


def test_s3_repository_configuration_when_using_default_aws_environment_variables():
    os.environ['AWS_S3_ENDPOINT_URL'] = ''
    os.environ['AWS_S3_ACCESS_KEY_ID'] = ''
    os.environ['AWS_S3_SECRET_ACCESS_KEY'] = ''

    repo = S3Repository()

    assert 'endpoint_url' not in repo.s3_session_config
    assert 'aws_access_key_id' not in repo.s3_session_config
    assert 'aws_secret_access_key' not in repo.s3_session_config


def test_s3_repository_configuration_when_custom_s3_variables_are_correctly_configured():
    os.environ['AWS_S3_ENDPOINT_URL'] = 'http://localhost:9999'
    os.environ['AWS_S3_ACCESS_KEY_ID'] = 'some-random-access-key'
    os.environ['AWS_S3_SECRET_ACCESS_KEY'] = 'some-random-secret'

    repo = S3Repository()

    assert 'endpoint_url' in repo.s3_session_config
    assert 'aws_access_key_id' in repo.s3_session_config
    assert 'aws_secret_access_key' in repo.s3_session_config


def test_s3_repository_get_objects_when_called(sample_json_file_url):
    url, content = sample_json_file_url
    repo = S3Repository()

    result = repo.open(url)

    assert result == content


def test_s3_repository_save_object_when_called(configure_minio_env_vars):
    url = Rfc1808Url.from_url(f's3://drift-bucket/{uuid4()}.json')
    content = {'SomeKey': 'SomeValue'}
    repo = S3Repository()

    repo.save(url, json.dumps(content))
    saved_file = repo.open(url)

    assert saved_file == content
