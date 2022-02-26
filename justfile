image_tag := "dev"

trivy_version := "0.24.0"
trivy_format := "table"
trivy_output := "/dev/stdout"
trivy_exit_code := "1"

build-docker-image:
  COMMIT_HASH={{image_tag}} docker-compose build app

publish-docker-image:
  COMMIT_HASH={{image_tag}} docker-compose push app

python-tests:
  docker-compose -f docker-compose.yaml -f docker-compose.tests.yaml up --exit-code-from app

helm-chart-tests: helm
  helm unittest -3 deploy/driftctl_exporter

scan-docker-image: trivy
  trivy image --severity CRITICAL \
              --no-progress \
              --exit-code {{trivy_exit_code}} \
              --format {{trivy_format}} \
              --output {{trivy_output}} \
              gcavalcante8808/driftctl-exporter:{{image_tag}}

trivy:
  #!/bin/bash
  if [[ -f /usr/local/bin/trivy ]] ; then exit 0; fi
  curl -L https://github.com/aquasecurity/trivy/releases/download/v{{trivy_version}}/trivy_{{trivy_version}}_Linux-64bit.tar.gz -o - | tar -xzvf - -C /usr/local/bin/
  chmod +x /usr/local/bin/trivy

helm:
  #!/bin/bash
  if [[ -f /usr/local/bin/helm ]] ; then exit 0; fi
  curl -S -L https://get.helm.sh/helm-v3.3.4-linux-amd64.tar.gz -o - | tar --strip-components 1 -xzvf - -C /tmp &> /dev/null
  sha256sum -c <(echo "34025bcbc9f543803aebf54ba3be8dabfb03407b7cc07497e8314ccd592ec973  /tmp/helm")
  mv /tmp/helm /usr/local/bin/helm
  chmod +x /usr/local/bin/helm
  helm plugin install https://github.com/quintush/helm-unittest --version 0.2.6
