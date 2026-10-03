"""Docker healthcheck: request the login page the way the reverse proxy would.

``urlopen`` raises for any error response, which makes the check fail.
"""

import os
import urllib.request

hosts = [h.strip() for h in os.environ.get("DJANGO_ALLOWED_HOSTS", "").split(",")]
host = next((h.lstrip(".") for h in hosts if h and h != "*"), "localhost")
request = urllib.request.Request(
    "http://127.0.0.1:8000/login/", headers={"Host": host, "X-Forwarded-Proto": "https"}
)
urllib.request.urlopen(request, timeout=4).close()
