build_base_local:
	docker build -t diploma-base -f ./contrib/docker/base/Dockerfile .

build_local: build_base_local
	docker compose --env-file=.env -f contrib/docker/docker-compose.yaml build

up_local:
	docker compose --env-file=.env -f contrib/docker/docker-compose.yaml up -d

build_up_local: build_local up_local

down_local:
	docker compose --env-file=.env -f contrib/docker/docker-compose.yaml down --remove-orphans

