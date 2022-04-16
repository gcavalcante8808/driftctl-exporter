### Metrics

The following metrics are exposed by the project:

| Metric Name                   | Description                                                                                                                               |
| ----------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------- |
| total_resources               | Number of resources found by driftctl, including cloud and terraform state resources.                                                     |
| total_changed                 | Number of resources that are declared on Iac but were changed externally.                                                                 |
| total_unmanaged               | Number of resources present on cloud provider but no declared on Iac.                                                                     |
| total_missing                 | Number of resources declared on Iac but missing from the cloud provider.                                                                  |
| total_managed                 | Number of resources fully managed by Iac.                                                                                                 |
| coverage                      | Relation between `total_managed` and `total_resources`.                                                                                   |
| managed_items_count_by_type   | Resources by type fully managed by Iac.                                                |
| unmanaged_items_count_by_type | Resources present on cloud provider but no declared on Iac.                                                 |
| missing_items_count_by_type   | Resources declared on Iac but missing from the cloud provider.                                                |
| changed_items_count_by_type   | Resources that are declared on Iac but were changed externally. |
