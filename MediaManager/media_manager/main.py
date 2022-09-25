import os
import subprocess

import uvicorn

from .manager import app


def _generate_cert(key_file: str, cert_file: str):
    subprocess.run(
        [
            "openssl",
            "req",
            "-subj",
            "/O=Duck Corp/C=AU/CN=example.com",
            "-new",
            "-x509",
            "-keyout",
            key_file,
            "-out",
            cert_file,
            "-days",
            "365",
            "-nodes",
        ],
        check=True,
    )


def run():
    loc = os.path.dirname(os.path.realpath(__file__))
    cwd = os.getcwd()

    print(f"script location: {loc}")
    print(f"cwd: {cwd}")

    ssl_key = f"{cwd}/key.pem"
    ssl_cert = f"{cwd}/cert.pem"

    if not os.path.exists(ssl_key):
        print("SSL Certificate not found, generating..")
        _generate_cert(ssl_key, ssl_cert)

    uvicorn.run(
        app, host="0.0.0.0", port=10443, ssl_keyfile=ssl_key, ssl_certfile=ssl_cert
    )
