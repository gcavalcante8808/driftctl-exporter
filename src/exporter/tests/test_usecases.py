import json
import os
import tempfile
from pathlib import Path
from unittest.mock import Mock

import pytest
from prometheus_client import REGISTRY

from exporter.domain import Rfc1808Url, DriftOutput
from exporter.repositories import S3Repository, DriftScanCmdRepository, DriftScanCmdException, \
    DriftScanInvalidResultError, ResultFileStorage
from exporter.usecases import scan_and_save_drift_on_s3_usecase, generate_metrics_from_drift_results_usecase


@pytest.fixture
def driftctl_output():
    pwd = Path(__file__).resolve().parent
    with open(f'{pwd}/fixtures/driftctl_output.json', 'rb') as drift:
        return drift.read()


@pytest.fixture
def drift_repository(driftctl_output):
    repo = DriftScanCmdRepository()
    repo.scan = Mock()
    repo.scan.return_value = driftctl_output

    return repo


@pytest.fixture
def s3_repository(driftctl_output):
    s3_repo = S3Repository()
    s3_repo.save = Mock()
    s3_repo.open = Mock()
    s3_repo.open.return_value = json.loads(driftctl_output)

    return s3_repo


@pytest.fixture
def filestorage_repository(driftctl_output):
    repo = ResultFileStorage()
    repo.save = Mock()
    repo.open = Mock()
    repo.open.return_value = json.loads(driftctl_output)

    return repo


def test_scan_and_save_a_drift_on_filestorage_when_all_configurations_are_valid(drift_repository,
                                                                                filestorage_repository,
                                                                                driftctl_output):
    _, file_path = tempfile.mkstemp()
    os.environ['RESULT_PATH'] = f'file://{file_path}'
    filestorage_config = Rfc1808Url.from_url(f'file://{file_path}')

    scan_and_save_drift_on_s3_usecase(drift_repository, filestorage_repository)

    assert drift_repository.scan.called
    assert filestorage_repository.save.called_with_args(**{'output_config': filestorage_config, 'content': driftctl_output})


def test_scan_and_save_a_drift_on_s3_when_all_configurations_are_valid(drift_repository, s3_repository,
                                                                       driftctl_output):
    os.environ['RESULT_PATH'] = 's3://another-bucket-to-hold/another-result-to-keep.json'
    s3_config = Rfc1808Url.from_url('s3://another-bucket-to-hold/another-result-to-keep.json')

    scan_and_save_drift_on_s3_usecase(drift_repository, s3_repository)

    assert drift_repository.scan.called
    assert s3_repository.save.called_with_args(**{'output_config': s3_config, 'content': driftctl_output})


def test_scan_and_save_a_drift_on_s3_fails_when_drift_scan_cmd_return_errors(drift_repository, s3_repository):
    drift_repository.scan.side_effect = DriftScanCmdException()

    with pytest.raises(DriftScanCmdException):
        scan_and_save_drift_on_s3_usecase(drift_repository, s3_repository)


def test_scan_and_save_a_drift_on_s3_fails_when_drift_scan_result_is_invalid(drift_repository, s3_repository):
    drift_repository.scan.side_effect = DriftScanInvalidResultError()

    with pytest.raises(DriftScanInvalidResultError):
        scan_and_save_drift_on_s3_usecase(drift_repository, s3_repository)


def test_generate_metrics_from_drift_integer_attributes(s3_repository, driftctl_output):
    drift = DriftOutput.from_json(json.loads(driftctl_output))
    url = Rfc1808Url.from_url('s3://another-bucket-to-hold/another-result-to-keep.json')
    generate_metrics_from_drift_results_usecase(s3_repository, url)

    total_resources = REGISTRY.get_sample_value('total_resources')
    total_changed = REGISTRY.get_sample_value('total_changed')
    total_unmanaged = REGISTRY.get_sample_value('total_unmanaged')
    total_missing = REGISTRY.get_sample_value('total_missing')
    total_managed = REGISTRY.get_sample_value('total_managed')
    coverage = REGISTRY.get_sample_value('coverage')

    assert drift.total_resources == total_resources
    assert drift.total_changed == total_changed
    assert drift.total_unmanaged == total_unmanaged
    assert drift.total_missing == total_missing
    assert drift.total_managed == total_managed
    assert drift.coverage == coverage


def test_generate_metrics_from_drift_managed_items_count_by_type(s3_repository, driftctl_output):
    drift = DriftOutput.from_json(json.loads(driftctl_output))
    url = Rfc1808Url.from_url('s3://another-bucket-to-hold/another-result-to-keep.json')

    generate_metrics_from_drift_results_usecase(s3_repository, url)
    aws_ami_metric_sample = REGISTRY.get_sample_value('managed_items_count_by_type', labels={'resource': 'aws_ami'})
    eip_association_metric_sample = REGISTRY.get_sample_value('managed_items_count_by_type',
                                                              labels={'resource': 'aws_eip_association'})

    assert drift.managed_items_count_by_type['aws_ami'] == aws_ami_metric_sample
    assert drift.managed_items_count_by_type['aws_eip_association'] == eip_association_metric_sample


def test_generate_metrics_from_drift_unmanaged_items_count_by_type(s3_repository, driftctl_output):
    drift = DriftOutput.from_json(json.loads(driftctl_output))
    url = Rfc1808Url.from_url('s3://another-bucket-to-hold/another-result-to-keep.json')

    generate_metrics_from_drift_results_usecase(s3_repository, url)
    aws_iam_policy_attachment_metric_sample = REGISTRY.get_sample_value('unmanaged_items_count_by_type', labels={
        'resource': 'aws_iam_policy_attachment'})
    aws_ebs_volume_sample = REGISTRY.get_sample_value('unmanaged_items_count_by_type',
                                                      labels={'resource': 'aws_ebs_volume'})

    aws_iam_role_sample = REGISTRY.get_sample_value('unmanaged_items_count_by_type',
                                                    labels={'resource': 'aws_iam_role'})

    assert drift.unmanaged_items_count_by_type['aws_iam_policy_attachment'] == aws_iam_policy_attachment_metric_sample
    assert drift.unmanaged_items_count_by_type['aws_ebs_volume'] == aws_ebs_volume_sample
    assert drift.unmanaged_items_count_by_type['aws_iam_role'] == aws_iam_role_sample


def test_generate_metrics_from_drift_missing_items_count_by_type(s3_repository, driftctl_output):
    drift = DriftOutput.from_json(json.loads(driftctl_output))
    url = Rfc1808Url.from_url('s3://another-bucket-to-hold/another-result-to-keep.json')

    generate_metrics_from_drift_results_usecase(s3_repository, url)
    aws_s3_bucket_metric_sample = REGISTRY.get_sample_value('missing_items_count_by_type',
                                                            labels={'resource': 'aws_s3_bucket'})

    assert drift.missing_items_count_by_type['aws_s3_bucket'] == aws_s3_bucket_metric_sample


def test_generate_metrics_from_drift_changed_items_count_by_type(s3_repository, driftctl_output):
    drift = DriftOutput.from_json(json.loads(driftctl_output))
    url = Rfc1808Url.from_url('s3://another-bucket-to-hold/another-result-to-keep.json')

    generate_metrics_from_drift_results_usecase(s3_repository, url)
    aws_s3_bucket_metric_sample = REGISTRY.get_sample_value('changed_items_count_by_type',
                                                            labels={'resource': 'aws_s3_bucket'})

    assert drift.changed_items_count_by_type['aws_s3_bucket'] == aws_s3_bucket_metric_sample
