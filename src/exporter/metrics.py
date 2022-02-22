from prometheus_client import Gauge


def get_metrics():
    total_resources = Gauge('total_resources', 'Drifctl metric: total_resources}.')
    total_changed = Gauge('total_changed', 'Drifctl metric: total_changed}.')
    total_unmanaged = Gauge('total_unmanaged', 'Drifctl metric: total_unmanaged}.')
    total_missing = Gauge('total_missing', 'Drifctl metric: total_missing}.')
    total_managed = Gauge('total_managed', 'Drifctl metric: total_managed}.')
    coverage = Gauge('coverage', 'Drifctl metric: coverage}.')
    managed_items_count_by_type = Gauge('managed_items_count_by_type', 'Resources found in IaC and in sync with remote',
                                        labelnames=['resource'])
    unmanaged_items_count_by_type = Gauge('unmanaged_items_count_by_type', 'Resources found in remote but not in IaC',
                                          labelnames=['resource'])
    missing_items_count_by_type = Gauge('missing_items_count_by_type', 'Resources found in IaC but not on remote',
                                        labelnames=['resource'])
    changed_items_count_by_type = Gauge('changed_items_count_by_type', 'Changes on managed resources.',
                                        labelnames=['resource'])

    return locals()


supported_metrics = get_metrics()
