# Sutitik Dispatcher

Reads RFID-Reader (which acts as HID Device (keyboard)), fetches media information from Media Manager, and dispatches the media to mopidy.

## Usage
```bash
sudo usermod -aG input $USER  # $USER has to be in the input group to be able to read input events
sudo pip install poetry
poetry install

poetry run python suitik_dispatcher
```
