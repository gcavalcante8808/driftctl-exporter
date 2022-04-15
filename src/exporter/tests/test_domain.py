import json
import tempfile
from collections import Counter
from pathlib import Path

import pytest

from exporter.domain import Rfc1808Url, DriftOutput


@pytest.fixture
def valid_s3_url():
    return "s3://some-bucket/some-path/some-nested-path/last-path"


@pytest.fixture
def valid_file_url():
    _, file_path = tempfile.mkstemp()
    return f'file:///tmp/some-path/last'


@pytest.fixture
def driftctl_json_output():
    pwd = Path(__file__).resolve().parent
    with open(f'{pwd}/fixtures/driftctl_output.json', 'rb') as drift:
        return json.load(drift)


def test_parse_output_from_s3_url_when_url_is_valid(valid_s3_url):
    s3_url = Rfc1808Url.from_url(valid_s3_url)

    assert 's3' == s3_url.scheme
    assert 'some-bucket' == s3_url.netloc
    assert 'some-path/some-nested-path/last-path' == s3_url.path


def test_parse_output_from_file_url_when_url_is_valid(valid_file_url):
    url = Rfc1808Url.from_url(valid_file_url)

    assert 'file' == url.scheme
    assert not url.netloc
    assert 'tmp/some-path/last' == url.path


def test_parse_output_from_url_when_url_is_INvalid(valid_s3_url):
    with pytest.raises(Exception):
        Rfc1808Url.from_url("")


def test_parse_drift_output(driftctl_json_output):
    output = DriftOutput.from_json(driftctl_json_output)

    assert output.total_resources == driftctl_json_output['summary']['total_resources']
    assert output.total_changed == driftctl_json_output['summary']['total_changed']
    assert output.total_unmanaged == driftctl_json_output['summary']['total_unmanaged']
    assert output.total_missing == driftctl_json_output['summary']['total_missing']
    assert output.total_managed == driftctl_json_output['summary']['total_managed']
    assert output.managed_items == driftctl_json_output.get('managed', [])
    assert output.unmanaged_items == driftctl_json_output.get('unmanaged', [])
    assert output.missing_items == driftctl_json_output.get('missing', [])
    assert output.differences_items == driftctl_json_output.get('differences', [])


def test_get_drift_as_dict(driftctl_json_output):
    drift = DriftOutput.from_json(driftctl_json_output)

    drift_as_dict = drift.as_dict()

    assert type(drift_as_dict) == dict
    assert 'total_resources' in drift_as_dict
    assert 'total_changed' in drift_as_dict
    assert 'total_unmanaged' in drift_as_dict
    assert 'total_missing' in drift_as_dict
    assert 'total_managed' in drift_as_dict


def test_get_drift_counters_for_managed_items_attributes_when_it_is_valid(driftctl_json_output):
    drift = DriftOutput.from_json(driftctl_json_output)

    managed_items_count_by_type = drift.managed_items_count_by_type

    assert type(managed_items_count_by_type) == Counter
    assert 2 == managed_items_count_by_type['aws_ami']
    assert 2 == managed_items_count_by_type['aws_eip_association']


def test_get_drift_counters_for_unmanaged_items_when_it_is_valid(driftctl_json_output):
    drift = DriftOutput.from_json(driftctl_json_output)

    unmanaged_items_count_by_type = drift.unmanaged_items_count_by_type

    assert type(unmanaged_items_count_by_type) == Counter
    assert 3 == unmanaged_items_count_by_type['aws_iam_policy_attachment']
    assert 3 == unmanaged_items_count_by_type['aws_ebs_volume']
    assert 2 == unmanaged_items_count_by_type['aws_iam_role']


def test_get_drift_counters_for_missing_items_attributes_when_it_is_valid(driftctl_json_output):
    drift = DriftOutput.from_json(driftctl_json_output)

    missing_items_count_by_type = drift.missing_items_count_by_type

    assert type(missing_items_count_by_type) == Counter
    assert 3 == missing_items_count_by_type['aws_s3_bucket']


def test_get_drift_counters_for_changed_items_attributes_when_it_is_valid(driftctl_json_output):
    drift = DriftOutput.from_json(driftctl_json_output)

    changed_items_count_by_type = drift.changed_items_count_by_type

    assert type(changed_items_count_by_type) == Counter
    assert 1 == changed_items_count_by_type['aws_s3_bucket']


def test_get_drift_counters_for_changed_items_when_there_is_none(driftctl_json_output):
    driftctl_json_output['differences'] = None
    driftctl_json_output['summary']['total_changed'] = 0
    drift = DriftOutput.from_json(driftctl_json_output)

    changed_items_count_by_type = drift.changed_items_count_by_type

    assert type(changed_items_count_by_type) == Counter
    assert 0 == changed_items_count_by_type['aws_s3_bucket']


def test_get_drift_counters_for_missing_items_when_there_is_none(driftctl_json_output):
    driftctl_json_output['missing'] = None
    driftctl_json_output['summary']['total_missing'] = 0
    drift = DriftOutput.from_json(driftctl_json_output)

    changed_items_count_by_type = drift.missing_items_count_by_type

    assert type(changed_items_count_by_type) == Counter
    assert 0 == changed_items_count_by_type['aws_s3_bucket']


def test_get_drift_counters_for_unmanaged_items_when_there_is_none(driftctl_json_output):
    driftctl_json_output['unmanaged'] = None
    driftctl_json_output['summary']['total_unmanaged'] = 0
    drift = DriftOutput.from_json(driftctl_json_output)

    items = drift.unmanaged_items_count_by_type

    assert type(items) == Counter
    assert 0 == items['aws_s3_bucket']


def test_get_drift_counters_for_managed_items_when_there_is_none(driftctl_json_output):
    driftctl_json_output['managed'] = None
    driftctl_json_output['summary']['total_managed'] = 0
    drift = DriftOutput.from_json(driftctl_json_output)

    items = drift.managed_items_count_by_type

    assert type(items) == Counter
    assert 0 == items['aws_s3_bucket']
