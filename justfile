image_tag := "latest"

build-docker-image:
  COMMIT_HASH={{image_tag}} docker-compose build app

