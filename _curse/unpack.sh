cd /home/aleh/diploma
tar -xvf diploma.tar
cd /home/aleh/diploma/diploma
docker network create a
docker pull hlohaus789/g4f:0.3.9.5
docker run --detach --name g4f hlohaus789/g4f:0.3.9.5
docker network connect a g4f
docker build -t diploma-base -f contrib/docker/base/Dockerfile .
docker compose --env-file=.env -f contrib/docker/docker-compose.prod.yaml up -d --build
