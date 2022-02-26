image_tag := "dev"

build-docker-image:
  COMMIT_HASH={{image_tag}} docker-compose build app

publish-docker-image:
  COMMIT_HASH={{image_tag}} docker-compose push app
