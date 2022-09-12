# Suitik Media Manager

Simple backend for Suitik Media Management. Uses FastAPI and SQLModel with sqlite database.

## Usage
```bash
sudo pip install poetry
poetry install

# generate SSL cert (for Web NFC in android)
openssl req -new -x509 -keyout key.pem -out cert.pem -days 365 -nodes

poetry run uvicorn media_manager.main:app --port 10443 --ssl-keyfile=./key.pem --ssl-certfile=./cert.pem
```

Available services:
- API Docs in `https://localhost:10443/api/v1/docs`
- Frontend in `https://localhost:10443`

Or open project in VS Code, press `F5` to start uvicorn with debugger support.