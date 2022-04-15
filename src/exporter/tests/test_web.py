import json
import os
from pathlib import Path
from uuid import uuid4

import pytest
from prometheus_client.parser import text_string_to_metric_families

from exporter.domain import Rfc1808Url, DriftOutput
from exporter.repositories import SmartyResultRepositoryFactory
from web import create_app


@pytest.fixture
def s3_config():
    filename = f'{uuid4()}.json'
    url = f's3://drift-bucket/{filename}'

    os.environ['AWS_S3_ENDPOINT_URL'] = 'http://s3:9000'
    os.environ['AWS_S3_ACCESS_KEY_ID'] = 'key'
    os.environ['AWS_S3_SECRET_ACCESS_KEY'] = 'some-secret'
    os.environ['RESULT_PATH'] = url

    return url


@pytest.fixture
def driftctl_output():
    pwd = Path(__file__).resolve().parent
    with open(f'{pwd}/fixtures/driftctl_output.json', 'rb') as drift:
        return drift.read()


@pytest.fixture
def sample_json_s3_url(s3_config, driftctl_output):
    url = Rfc1808Url.from_url(s3_config)
    repo = SmartyResultRepositoryFactory.get_repository_by_scheme_url(url)

    repo.save(url, driftctl_output)

    return url, json.loads(driftctl_output)


@pytest.fixture
def filestorage_config():
    pwd = Path(__file__).resolve().parent
    url = f'file://{pwd}/fixtures/driftctl_output.json'

    os.environ['RESULT_PATH'] = url

    return url


@pytest.fixture
def sample_json_filestorage_url(filestorage_config, driftctl_output):
    url = Rfc1808Url.from_url(filestorage_config)

    return url, json.loads(driftctl_output)


async def test_that_supported_metrics_are_being_computed_and_exposed_when_using_s3_repo(aiohttp_client,
                                                                                        sample_json_s3_url, loop):
    app = await create_app()
    client = await aiohttp_client(app)
    _, content = sample_json_s3_url
    drift = DriftOutput.from_json(content)
    supported_metrics = drift.as_dict().keys()

    response = await client.get('/metrics')
    assert response.status == 200
    text = await response.text()
    computed_metrics = text_string_to_metric_families(text)

    supported_metrics_samples = []
    for family in computed_metrics:
        for sample in family.samples:
            if sample.name in supported_metrics:
                supported_metrics_samples.append(sample)
                assert drift.as_dict()[sample.name] == sample.value

    assert supported_metrics_samples


async def test_that_supported_metrics_are_being_computed_and_exposed_when_using_file_repo(aiohttp_client,
                                                                                          sample_json_filestorage_url,
                                                                                          loop):
    app = await create_app()
    client = await aiohttp_client(app)
    _, content = sample_json_filestorage_url
    drift = DriftOutput.from_json(content)
    supported_metrics = drift.as_dict().keys()

    response = await client.get('/metrics')
    assert response.status == 200
    text = await response.text()
    computed_metrics = text_string_to_metric_families(text)

    supported_metrics_samples = []
    for family in computed_metrics:
        for sample in family.samples:
            if sample.name in supported_metrics:
                supported_metrics_samples.append(sample)
                assert drift.as_dict()[sample.name] == sample.value

    assert supported_metrics_samples
