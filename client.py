#!/usr/bin/env python3
import http.client, sys, urllib.parse, os, ssl

VERSION = "1.5.0"

# Checking the client's version can't be a CLI flag: this script forwards
# *everything* it's invoked with -- symlink name and all arguments -- to
# the server as the remote command to run. A `--version` flag would be
# indistinguishable from someone legitimately trying to check the
# *remote* command's version (e.g. a `python` symlink run as
# `python --version`), so it's an env var instead, consistent with how
# REMOTE_EXEC_TLS and REMOTE_EXEC_ALLOWED are already configured here.
if os.environ.get("REMOTE_EXEC_CLIENT_VERSION", "") == "1":
    print(f"remote-exec-client {VERSION}")
    sys.exit(0)

host = "192.168.56.1:8000"

# Optional TLS. Set REMOTE_EXEC_TLS=1 to connect via HTTPS instead of HTTP.
# Set REMOTE_EXEC_TLS_INSECURE=1 to skip certificate verification — needed
# for self-signed certs (typical for local/dev deployments); never set this
# when connecting over an untrusted network.
use_tls = os.environ.get("REMOTE_EXEC_TLS", "") == "1"
insecure = os.environ.get("REMOTE_EXEC_TLS_INSECURE", "") == "1"

if use_tls:
    ctx = ssl.create_default_context()
    if insecure:
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
    conn = http.client.HTTPSConnection(host, context=ctx)
else:
    conn = http.client.HTTPConnection(host)

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
