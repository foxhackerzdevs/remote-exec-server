#!/usr/bin/env python3
from http.server import BaseHTTPRequestHandler, HTTPServer
import subprocess, urllib.parse, shlex, os

class MyHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length).decode("utf-8")

        # Decode URL path and split into command parts
        raw_path = urllib.parse.unquote(self.path.lstrip("/"))
        cmd_parts = shlex.split(raw_path)

        # Normalize first element to basename (safe fallback)
        cmd_parts[0] = os.path.basename(cmd_parts[0])
        print("Executing:", cmd_parts)

        try:
            result = subprocess.run(
                cmd_parts,
                input=body.encode(),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True
            )
            output = result.stdout.decode()
        except subprocess.CalledProcessError as e:
            output = f"Error:\n{e.stderr.decode()}"
        except FileNotFoundError:
            output = f"Error: command not found: {cmd_parts[0]}"

        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(output.encode())

if __name__ == "__main__":
    server = HTTPServer(("0.0.0.0", 8000), MyHandler)
    print("Serving on 0.0.0.0:8000")
    server.serve_forever()

