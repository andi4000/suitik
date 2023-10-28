# Suitik

RFID-Card-based Music Player inspired by tonies(R) Toniebox.

## User Guide
- Upload mp3 file via Web Interface at `https://<target_host>:10443`
    - Accept the self-signed certificate warning


## Installation
TODO

## Tested on
### Software
- Raspberry Pi Buster (Debian 10)
- Python 3.7 (Version shipped with Buster)

### Hardware
- Raspberry Pi 3B Plus
- Neuftech 13.56 MHz RFID Card Reader
- RFID MIFARE Classic 1K Cards --> Readable on Android Smartphones


## Development Environment
```bash
# On Raspberry Pi
make dev-install
make install-mopidy
```
