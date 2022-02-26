image_tag := "dev"

trivy_version := "0.24.0"
trivy_format := "table"
trivy_output := "/dev/stdout"
trivy_exit_code := "1"

build-docker-image:
  COMMIT_HASH={{image_tag}} docker-compose build app

publish-docker-image:
  COMMIT_HASH={{image_tag}} docker-compose push app

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
  chmod +x trivy
