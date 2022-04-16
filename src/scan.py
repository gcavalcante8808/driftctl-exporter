import os

from exporter.repositories import DriftScanCmdRepository, SmartyResultRepositoryFactory
from exporter.usecases import scan_and_save_drift_on_storage_usecase
from exporter.domain import Rfc1808Url

DCTL_FROM = os.environ["DCTL_FROM"]

RESULT_PATH = os.environ["RESULT_PATH"]


url = Rfc1808Url.from_url(RESULT_PATH)
drift_repository = DriftScanCmdRepository()
result_repo = SmartyResultRepositoryFactory.get_repository_by_scheme_url(url)

if __name__ == '__main__':
    scan_and_save_drift_on_storage_usecase(drift_repository, result_repo)
