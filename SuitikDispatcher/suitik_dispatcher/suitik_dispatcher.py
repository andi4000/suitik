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


class SuitikDispatcher:
    def __init__(self, *, rpc_url: str = None):
        self._rfid_reader = None
        self._client = None

        self._rpc_url = "http://localhost:6680/mopidy/rpc"
        if rpc_url is not None:
            self._rpc_url = rpc_url

    def _init_rfid_reader(self):
        logging.info("Looking for RFID Reader..")

        devices = [InputDevice(path) for path in list_devices()]
        logging.info("Found total %d devices", len(devices))

        for dev in devices:
            if dev.name.lower().endswith("ic reader"):
                logging.info("Reader found: %s", dev)
                self._rfid_reader = dev
                break

        if not self._rfid_reader:
            logging.error("Device not found, permission problem?")
            sys.exit(-1)

    def _init_mopidy_client(self):
        logging.info("Initializing connection to mopidy: %s", self._rpc_url)
        self._client = MopidyClient(self._rpc_url)
        if not self._client.is_connected():
            logging.error("Connection failed: %s", self._rpc_url)
            sys.exit(-1)

        logging.info("Mopidy connection OK.")

    def init(self):
        self._init_rfid_reader()
        self._init_mopidy_client()

    def run(self):
        logging.info("Entering main loop..")
        with self._rfid_reader.grab_context():
            card_id = ""
            for event in self._rfid_reader.read_loop():
                if event.type == ecodes.EV_KEY and event.value == KeyEvent.key_up:
                    try:
                        key = SCANCODES[event.code]
                        card_id += str(key)
                    except:
                        # This block will be executed when RFID-Reader sends KEY_ENTER
                        logging.info("Card ID: %s", card_id)
                        resp = requests.get(
                            f"http://localhost:8000/cards/{card_id}/songs"
                        )
                        card_id = ""
                        if resp.status_code == 200:
                            file_uris = [resp.json()[0]["uri"]]
                            print(file_uris)
                            self._client.clear_tracks()
                            self._client.add_tracks(file_uris)
                            self._client.play()
                        else:
                            logging.error("Could not find any song.")
