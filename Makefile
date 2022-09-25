SHELL := /bin/bash

.PHONY: help

# From: https://marmelab.com/blog/2016/02/29/auto-documented-makefile.html
help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk \
		'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

dev-install:  ## Install dev environment
	@echo "==> Preparing environment"
	@which pip3 && echo "pip OK." || { echo "pip not found, installing.."; \
		sudo apt install -y python3-pip; }
	@source ~/.profile && which poetry && echo "poetry OK." || { echo \
		"poetry not found, installing.."; pip3 install poetry; }
	@source ~/.profile && cd MediaManager; poetry install
	@source ~/.profile && cd SuitikDispatcher; poetry install


install-mopidy:  ## install mopidy from apt for raspberry pi
	@sudo mkdir -p /usr/local/share/keyrings
	@sudo wget -q -O /usr/local/share/keyrings/mopidy-archive-keyring.gpg \
		https://apt.mopidy.com/mopidy.gpg
	@sudo wget -q -O /etc/apt/sources.list.d/mopidy.list \
		https://apt.mopidy.com/buster.list
	@sudo apt update
	@sudo apt install -y mopidy


dev-run-manager:  ## Run Suitik Media Manager
	@echo "==> Creating key if not exist"
	@cd MediaManager; test -f key.pem || \
		openssl req -subj "/O=Duck Corp/C=AU/CN=example.com" -new -x509 \
		-keyout key.pem -out cert.pem -days 365 -nodes
	@echo "==> Launching Media Manager"
	@cd MediaManager; poetry run uvicorn media_manager.manager:app --reload \
		--host "0.0.0.0" --port 10443 \
		--ssl-keyfile=./key.pem --ssl-certfile=./cert.pem

dev-run-dispatcher:  ## Run Suitik Dispatcher
	@echo "==> Launching dispatcher"
	@cd SuitikDispatcher; poetry run suitik_dispatcher

dev-run-mopidy:  ## Run Mopidy
	@echo "==> Launching mopidy"
	source venv/bin/activate && mopidy -v
