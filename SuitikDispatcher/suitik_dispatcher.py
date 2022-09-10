import sys
import logging

import requests
from evdev import InputDevice, list_devices, ecodes, KeyEvent

from mopidy_client import MopidyClient

logging.basicConfig(level=logging.INFO)

# From linux/input-event-codes.h
SCANCODES = {
    2: 1,
    3: 2,
    4: 3,
    5: 4,
    6: 5,
    7: 6,
    8: 7,
    9: 8,
    10: 9,
    11: 0,
}

rfid_reader = None

logging.info("Looking for RFID Reader..")

devices = [InputDevice(path) for path in list_devices()]
logging.info("Found total %d devices", len(devices))

for dev in devices:
    if dev.name.lower().endswith("ic reader"):
        logging.info("Reader found: %s", dev)
        rfid_reader = dev
        break

if not rfid_reader:
    logging.error("Device not found, permission problem?")
    sys.exit(-1)

client = MopidyClient("http://localhost:6680/mopidy/rpc")

with rfid_reader.grab_context():
    card_id = ""
    for event in rfid_reader.read_loop():
        if event.type == ecodes.EV_KEY and event.value == KeyEvent.key_up:
            try:
                key = SCANCODES[event.code]
                card_id += str(key)
            except:
                # This block will be executed when RFID-Reader sends KEY_ENTER
                logging.info("Card ID: %s", card_id)
                resp = requests.get(f"http://localhost:8000/cards/{card_id}/songs")
                card_id = ""
                if resp.status_code == 200:
                    file_uris = [resp.json()[0]["uri"]]
                    print(file_uris)
                    client.clear_tracks()
                    client.add_tracks(file_uris)
                    client.play()
                else:
                    logging.error("Could not find any song.")
