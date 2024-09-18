# Colors
_END		= \033[0m
_INFO		= \033[1;33m
_BUILD		= \033[1;32m
_REMOVE		= \033[1;31m

# TODO: add clean of db and dep

.PHONY: all
all: build up

.PHONY: build
build:
#	@mkdir -p ./db/postgres
	@docker compose build

.PHONY: up
up:
	@docker compose up -d

.PHONY: down
down:
	@docker compose down

.PHONY: clean
clean:
	@docker compose down --rmi all --volumes --remove-orphans
	@docker stop $(docker ps -qa) 2>/dev/null || true
	@docker rm $(docker ps -qa) 2>/dev/null || true
	@docker rmi $(docker images -qa) 2>/dev/null || true
	@docker volume rm $(docker volume ls -q) 2>/dev/null || true
	@docker network rm $(docker network ls -q) 2>/dev/null || true

.PHONY: reload
reload: down up

.PHONY: re
re: clean all

.PHONY: info
info:
	@echo "${_INFO}======================= COMPOSE ========================${_END}"
	@docker compose ps
	@echo "\n${_INFO}======================== IMAGES ========================${_END}"
	@docker images
	@echo "\n${_INFO}====================== CONTAINERS ======================${_END}"
	@docker ps -a
	@echo "\n${_INFO}======================== VOLUMES =======================${_END}"
	@docker volume ls
	@echo "\n${_INFO}======================== NETWORKS ======================${_END}"
	@docker network ls

.PHONY: help
help:
	@echo "Usage: make [OPTION]"
	@echo "Options:"
	@echo "  all       Build and run containers"
	@echo "  build     Build containers"
	@echo "  up        Run containers"
	@echo "  down      Stop containers"
	@echo "  clean     Stop and remove containers, images, volumes and networks"
	@echo "  fclean    Stop and remove containers, images, volumes and networks"
	@echo "            and clean all files"
	@echo "  re        Run fclean and all"
	@echo "  info      Show containers, images, volumes and networks"
	@echo "  help      Show this help"

.DEFAULT_GOAL := help
