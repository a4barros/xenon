.DEFAULT_GOAL := help

.PHONY: help up test down logs run run-db

help: ## Display this help message
		@awk -F ':.*?## ' '/^[a-zA-Z_-]+:.*?##/ {printf "\033[36m%-25s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

up: ## Rebuild and restart server
		docker compose up --build -d app db

down: ## Kill server
		docker compose down

run-db: ## Run just the database
		docker compose up -d db

test: ## Run backend and frontend tests
		python -m unittest discover -s tests -v
		node --experimental-default-type=module --test front/tests/*.test.mjs