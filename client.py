#!/usr/bin/env python3
import http.client, sys, urllib.parse

host = "192.168.56.1:8000"
conn = http.client.HTTPConnection(host)  # use HTTPSConnection only if server supports TLS

# Encode arguments safely
path = "/" + urllib.parse.quote(sys.argv[0] + " " + " ".join(sys.argv[1:]))

# Read stdin as bytes to support non-Latin-1 characters (e.g. Unicode)
body = sys.stdin.buffer.read()

# Send request with explicit UTF-8 content type
conn.request("POST", path, body=body, headers={"Content-Type": "text/plain; charset=utf-8"})

# Print response
response = conn.getresponse()
print(response.read().decode())

