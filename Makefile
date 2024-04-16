# TODO: add clean of db and dep + cli colors and logs

.PHONY: all
all: build up

.PHONY: build
build:
#	@mkdir -p ./db/postgres
	@docket compose build

# TODO: add an option for detach
.PHONY: up
up:
	@docket compose up

.PHONY: down
down:
	@docket compose down --volumes

.PHONY: clean
clean:
	@docker compose down --rmi all --volumes --remove-orphans
	@docker stop $(docker ps -qa) 2>/dev/null || true
	@docker rm $(docker ps -qa) 2>/dev/null || true
	@docker rmi $(docker images -qa) 2>/dev/null || true
	@docker volume rm $(docker volume ls -q) 2>/dev/null || true
	@docker network rm $(docker network ls -q) 2>/dev/null || true

.PHONY: fclean
fclean: clean
#	@rm -rf ./data/postgres
#	@rm -rf backend/node_modules && rm -rf backend/dist || true
#	@rm -rf frontend/node_modules && rm -rf frontend/dist || true
#	@rm backend/uploads/* || true

.PHONY: re
re: fclean all

.PHONY: info
info:
	@echo "======================= COMPOSE ========================"
	@docker compose ps
	@echo "\n======================== IMAGES ========================"
	@docker images
	@echo "\n====================== CONTAINERS ======================"
	@docker ps -a
	@echo "\n======================== VOLUMES ======================="
	@docker volume ls
	@echo "\n======================== NETWORKS ======================"
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
