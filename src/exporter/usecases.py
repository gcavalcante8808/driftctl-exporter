import os

from exporter.domain import Rfc1808Url, DriftOutput
from exporter.presenters import present_drift_int_attr_as_prometheus_gauge, \
    present_drift_counter_attr_as_prometheus_gauge
from exporter.repositories import DriftScanCmdException, DriftScanInvalidResultError
from exporter.utils.json_logger import logger


def scan_and_save_drift_on_storage_usecase(drift_repository,
                                           s3_repository,
                                           ):
    logger.info("Starting a Drift Scan.")
    try:
        drift_result = drift_repository.scan()
    except DriftScanCmdException as ctx:
        logger.fatal(f"Drift Scan didn't ran successfully. Check the output for more details.\n str{ctx}")
        raise
    except DriftScanInvalidResultError as ctx:
        logger.fatal(f"Drift Scan result is not valid. Check the output for more details.\n str{ctx}")
        raise

    logger.info("Drift Scan complete successfully. Sending the result for S3 Repository.")
    s3_repository.save(output_config=Rfc1808Url.from_url(os.getenv('RESULT_PATH')), content=drift_result)

    logger.info("Drift Scan Report saved. Task Finished.")


def generate_metrics_from_drift_results_usecase(s3_repository, url):
    drift_result = s3_repository.open(url)
    drift = DriftOutput.from_json(drift_result)
    metrics = drift.integer_attributes_suitable_for_metrics

    for metric in metrics:
        value = getattr(drift, metric)
        present_drift_int_attr_as_prometheus_gauge(metric, value)

    composite_metrics = drift.counter_attributes_suitable_for_metrics

    for metric in composite_metrics:
        value = getattr(drift, metric)
        for resource in value.keys():
            present_drift_counter_attr_as_prometheus_gauge(metric, resource, value[resource])
