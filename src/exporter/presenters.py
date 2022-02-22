def present_drift_int_attr_as_prometheus_gauge(metric, value):
    from exporter.metrics import supported_metrics

    metric = supported_metrics[metric]
    metric.set(value)


def present_drift_counter_attr_as_prometheus_gauge(metric, resource, value):
    from exporter.metrics import supported_metrics

    metric = supported_metrics[metric]
    metric.labels(resource).set(value)
