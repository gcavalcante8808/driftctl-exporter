## Driftctl Exporter

[![codecov](https://codecov.io/gh/gcavalcante8808/driftctl-exporter/branch/main/graph/badge.svg?token=U7XVngTS3G)](https://codecov.io/gh/gcavalcante8808/driftctl-exporter)
[![Actions Status](https://github.com/gcavalcante8808/driftctl-exporter/workflows/BuildNTest/badge.svg)](https://github.com/gcavalcante8808/driftctl-exporter/actions)
[![Actions Status](https://github.com/gcavalcante8808/driftctl-exporter/workflows/TrivyScan/badge.svg)](https://github.com/gcavalcante8808/driftctl-exporter/actions)

This project aims export the driftctl scan result in the prometheus exporter/openmetrics format, making it suitable to monitoring possible drifts on a environment.

This project doesn't have a direct relation with [GitHub - snyk/driftctl: Detect, track and alert on infrastructure drift](https://github.com/snyk/driftctl), but it uses the scan feature and the result created to expose it as basic metrics and some other metrics (like counts by resource type).

#### How it Works?

Actually, the workflow consists in 3 steps:

1. The `scan.py` runs `drifctl scan` command, whom reads the tfstate configured by the `DCTL_FROM` environment variable, compare with the cloud resources and persist the scan result in json format to the s3 bucket specified in `RESULT_PATH` environment variable;

2. The `web.py` expose the `/metrics` endpoint which scrapes the scan result from s3 every time a get request is received;

3. Scrape the values using some compatible application (prometheus, opentelemetry, datadog agent, etc).

Author
------

Author: Gabriel Abdalla Cavalcante Silva (gabriel.cavalcante88@gmail.com)
