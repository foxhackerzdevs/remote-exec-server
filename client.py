#!/usr/bin/env python3
import http.client, sys, urllib.parse

host = "192.168.56.1:8000"
conn = http.client.HTTPConnection(host)  # use HTTPSConnection only if server supports TLS

# Encode arguments safely — avoid trailing space when no args are given
cmd_str = sys.argv[0]
if len(sys.argv) > 1:
    cmd_str += " " + " ".join(sys.argv[1:])
path = "/" + urllib.parse.quote(cmd_str)

# Read stdin as bytes to support non-Latin-1 characters (e.g. Unicode)
body = sys.stdin.buffer.read()

# Send request with explicit UTF-8 content type
conn.request("POST", path, body=body, headers={"Content-Type": "text/plain; charset=utf-8"})

# Stream response line by line as it arrives
response = conn.getresponse()
for line in response:
    sys.stdout.buffer.write(line)
    sys.stdout.buffer.flush()

