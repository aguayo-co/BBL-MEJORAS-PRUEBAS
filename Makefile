.DEFAULT_GOAL := help

define purpleecho
      @tput setaf 5
      @echo $1
      @tput sgr0
endef

define blueecho
      @tput setaf 6
      @echo $1
      @tput sgr0
endef


.PHONY: start
start: ## Start DockerSync and Project containers.
	ln -fs docker-compose.docker-sync.yml docker-compose.override.yml
	@docker-sync start
	@docker-compose up -d

.PHONY: stop
stop: ## Stop Project DockerSync and containers.
	@docker-compose down
	@docker-sync stop
	ln -fs docker-compose.volumes.yml docker-compose.override.yml

.PHONY: help
help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-16s\033[0m %s\n", $$1, $$2}'
