from typing import List, Dict
import logging

import requests

logging.basicConfig(level=logging.INFO)


class MopidyClient:
    """Blocking JSON-RPC Mopidy Client"""

    def __init__(self, server_url: str):
        """
        Args:
            server_url (str): e.g. http://localhost:6680/mopidy/rpc

        """
        self._server_url = server_url
        self._id = 0

    def rpc(self, method: str, params: Dict = None):
        payload = {
            "jsonrpc": "2.0",
            "id": self._id,
            "method": method,
        }

        if params:
            payload["params"] = params

        logging.debug("Sending JSON-RPC Payload: %s", payload)
        resp = requests.post(self._server_url, json=payload)
        self._id += 1

        return resp

    def is_connected(self):
        try:
            resp = self.rpc("core.tracklist.get_version")
            return resp.status_code == 200
        except requests.ConnectionError:
            return False

    def add_tracks(self, file_uris: List[str]):
        return self.rpc("core.tracklist.add", {"uris": file_uris})

    def clear_tracks(self):
        return self.rpc("core.tracklist.clear")

    def play(self):
        return self.rpc("core.playback.play")

    def stop(self):
        return self.rpc("core.playback.stop")
