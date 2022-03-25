#### How it Works?

Actually, the workflow consists in 3 steps:

1. The `scan.py` runs `drifctl scan` command, whom reads the tfstate configured by the `DCTL_FROM` environment variable, compare with the cloud resources and persist the scan result in json format to the s3 bucket specified in `RESULT_PATH` environment variable;
  
2. The `web.py` expose the `/metrics` endpoint which scrapes the scan result from s3 every time a get request is received;
  
3. Scrape the values using some compatible application (prometheus, opentelemetry, datadog agent, etc).
  

### Architecture - Components

The drifctl exporter consists in two main python scripts: **scan.py** and **web.py**, which compound the following workflow:

![drifctlexporter](file:///home/arthas/PycharmProjects/personal/driftctl-exporter/docs/drifctl_exporter.png)

> For Kubernetes/Helm version, the scan.py is an `init_container` that will run in the first time the pods starts. From there on, there is a Cronjob that runs the scan every day on 4am.

##### Scan.py

The **scan.py** script relies heavily on [GitHub - snyk/driftctl: Detect, track and alert on infrastructure drift](https://github.com/snyk/driftctl) to generate the drift result in json format.

As the `drifctl scan` can have some big execution times (depending on how many resources are you comparing), it is safe to assume the "batch" nature of the script; actually I think it should be executed some times in a day but not more often.

It executes the `driftctl scan` using the `DCTL_FROM` environment variable to read the `tfstate` file (or files) and compare the resources described in the tfstate with those created on the cloud; after that, it persist the `driftctl scan` json result in a s3 bucket specified by the `RESULT_PATH` environment variable.

##### Web.py

The **web.py** actually reads the drifctl scan result from the S3 specified on the `RESULT_PATH` environment variables and expose the information in prometheus/openmetrics format at the `/metrics` endpoint.

> The web.py component expects that the s3 url defined in `RESULT_PATH` actually have the `driftctl scan` output in json format. If you don't have a result file yet, generate one by running the `scan.py` first.