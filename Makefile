SHELL := /bin/bash

.PHONY: help

# From: https://marmelab.com/blog/2016/02/29/auto-documented-makefile.html
help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk \
		'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

dev-install:  ## Install dev environment
	@echo "==> Preparing environment"
	@which pip3 || echo "pip not found, installing.." && sudo apt install -y \
		python3-pip
	@source ~/.profile && which poetry || echo "poetry not found, installing" \
		&& pip3 install poetry
	@source ~/.profile && cd MediaManager; poetry install
	@source ~/.profile && cd SuitikDispatcher; poetry install


dev-run-manager:  ## Run Suitik Media Manager
	@echo "==> Creating key if not exist"
	@cd MediaManager; test -f key.pem || \
		openssl req -subj "/O=Duck Corp/C=AU/CN=example.com" -new -x509 \
		-keyout key.pem -out cert.pem -days 365 -nodes
	@echo "==> Launching Media Manager"
	@cd MediaManager; poetry run uvicorn media_manager.main:app --reload \
		--host "0.0.0.0" --port 10443 \
		--ssl-keyfile=./key.pem --ssl-certfile=./cert.pem

dev-run-dispatcher:  ## Run Suitik Dispatcher
	@echo "==> Launching dispatcher"
	@cd SuitikDispatcher; poetry run python suitik_dispatcher

dev-run-mopidy:  ## Run Mopidy
	@echo "==> Launching mopidy"
	source venv/bin/activate && mopidy -v
