import os

from exporter.domain import Rfc1808Url
from exporter.repositories import DriftScanCmdRepository, ResultFileStorage


def test_scan_passes_correct_arguments_to_scan_usecase():
    os.environ['DCTL_FROM'] = 'tfstate://./exporter/tests/fixtures/terraform.tfstate'
    os.environ['RESULT_PATH'] = 'file:///data/results.json'

    from scan import url, drift_repository, result_repo

    assert type(url) == Rfc1808Url
    assert type(drift_repository) == DriftScanCmdRepository
    assert type(result_repo) == ResultFileStorage
