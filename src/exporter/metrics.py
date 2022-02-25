from prometheus_client import Gauge


def get_metrics():
    total_resources = Gauge('total_resources', 'Number of resources found by driftctl.')
    total_changed = Gauge('total_changed', 'Number of resources that are declared on Iac but were changed externally.')
    total_unmanaged = Gauge('total_unmanaged', 'Number of resources present on cloud provider but no declared on Iac.')
    total_missing = Gauge('total_missing', 'Number of resources declared on Iac but missing from the cloud provider.')
    total_managed = Gauge('total_managed', 'Number of resources fully managed by Iac.')
    coverage = Gauge('coverage', 'Relation between `total_managed` and `total_resources`.')
    managed_items_count_by_type = Gauge('managed_items_count_by_type',
                                        'Number of resources by type fully managed by Iac. '
                                        'Eg: number of `aws_s3_bucket` and so on.',
                                        labelnames=['resource'])
    unmanaged_items_count_by_type = Gauge('unmanaged_items_count_by_type',
                                          'Number of resources by type fully managed by Iac. '
                                          'Eg: number of `aws_iam_user` and so on.',
                                          labelnames=['resource'])
    missing_items_count_by_type = Gauge('missing_items_count_by_type',
                                        'Number of resources by type fully managed by Iac. '
                                        'Eg: number of `aws_sqs_queue` and so on.',
                                        labelnames=['resource'])
    changed_items_count_by_type = Gauge('changed_items_count_by_type',
                                        'Number of resources that are declared on Iac but were changed externally, '
                                        'by resource type. Eg: number of `aws_dynamodb_table` and so on.',
                                        labelnames=['resource'])

    return locals()


supported_metrics = get_metrics()
