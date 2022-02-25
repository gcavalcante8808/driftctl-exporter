import os

from exporter.repositories import S3Repository, DriftScanCmdRepository
from exporter.usecases import scan_and_save_drift_on_s3_usecase

DCTL_FROM = os.environ["DCTL_FROM"]

RESULT_PATH = os.environ["RESULT_PATH"]


drift_repository = DriftScanCmdRepository()
s3_repository = S3Repository()

scan_and_save_drift_on_s3_usecase(drift_repository, s3_repository)
