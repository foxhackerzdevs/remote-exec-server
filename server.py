#!/usr/bin/env python3
from http.server import BaseHTTPRequestHandler, HTTPServer
import subprocess, urllib.parse, shlex, os

class MyHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length)

        # Decode URL path and split into command parts
        raw_path = urllib.parse.unquote(self.path.lstrip("/"))
        cmd_parts = shlex.split(raw_path)

        # Normalize first element to basename (safe fallback)
        cmd_parts[0] = os.path.basename(cmd_parts[0])
        print("Executing:", cmd_parts)

        try:
            process = subprocess.Popen(
                cmd_parts,
                input=body,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )

            self.send_response(200)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.send_header("Transfer-Encoding", "chunked")
            self.end_headers()

            # Stream stdout line by line as it's produced
            for line in process.stdout:
                chunk = line
                self.wfile.write(f"{len(chunk):X}\r\n".encode())
                self.wfile.write(chunk)
                self.wfile.write(b"\r\n")
                self.wfile.flush()

            process.wait()

            # Send stderr as final chunk if process failed
            if process.returncode != 0:
                err = process.stderr.read()
                if err:
                    error_msg = f"Error:\n{err.decode('utf-8', errors='replace')}".encode("utf-8")
                    self.wfile.write(f"{len(error_msg):X}\r\n".encode())
                    self.wfile.write(error_msg)
                    self.wfile.write(b"\r\n")

            # Terminate chunked transfer
            self.wfile.write(b"0\r\n\r\n")
            self.wfile.flush()

        except FileNotFoundError:
            self.send_response(200)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.end_headers()
            self.wfile.write(f"Error: command not found: {cmd_parts[0]}\n".encode())

    def log_message(self, format, *args):
        # Suppress default HTTP access log noise
        print(f"[{self.address_string()}] {format % args}")

if __name__ == "__main__":
    server = HTTPServer(("0.0.0.0", 8000), MyHandler)
    print("Serving on 0.0.0.0:8000")
    server.serve_forever()

