SHELL := /bin/bash

dev-run-manager:
	@echo "==> Creating key if not exist"
	@cd MediaManager; test -f key.pem || \
		openssl req -subj "/O=Duck Corp/C=AU/CN=example.com" -new -x509 \
		-keyout key.pem -out cert.pem -days 365 -nodes
	@echo "==> Launching Media Manager"
	@cd MediaManager; poetry run uvicorn media_manager.main:app --reload \
		--host "0.0.0.0" --port 10443 \
		--ssl-keyfile=./key.pem --ssl-certfile=./cert.pem

dev-run-dispatcher:
	@echo "==> Launching dispatcher"
	@cd SuitikDispatcher; poetry run python suitik_dispatcher

dev-run-mopidy:
	@echo "==> Launching mopidy"
	source venv/bin/activate && mopidy -v
