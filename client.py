#!/usr/bin/env python3
import http.client, sys, urllib.parse

host = "192.168.56.1:8000"
conn = http.client.HTTPConnection(host)  # use HTTPSConnection only if server supports TLS

# Encode arguments safely
path = "/" + urllib.parse.quote(sys.argv[0] + " " + " ".join(sys.argv[1:]))

# Read stdin
body = sys.stdin.read()

# Send request
conn.request("POST", path, body=body)

# Print response
response = conn.getresponse()
print(response.read().decode())

