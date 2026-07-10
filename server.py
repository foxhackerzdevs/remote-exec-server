#!/usr/bin/env python3
from http.server import BaseHTTPRequestHandler, HTTPServer
import subprocess, urllib.parse, shlex, os, threading, queue, ssl

# Optional command whitelist. Set the REMOTE_EXEC_ALLOWED environment variable
# to a comma-separated list of allowed command names (e.g. "gp,python,node").
# If unset or empty, all commands are allowed (backward-compatible default —
# strongly recommended to set this in any network-exposed deployment).
_allowed_env = os.environ.get("REMOTE_EXEC_ALLOWED", "")
ALLOWED = {c.strip() for c in _allowed_env.split(",") if c.strip()}

# Optional TLS. Set REMOTE_EXEC_TLS_CERT and REMOTE_EXEC_TLS_KEY to paths of a
# certificate and private key (PEM format) to serve over HTTPS instead of HTTP.
# If either is unset, the server runs in plain HTTP (backward-compatible default).
TLS_CERT = os.environ.get("REMOTE_EXEC_TLS_CERT", "")
TLS_KEY  = os.environ.get("REMOTE_EXEC_TLS_KEY", "")

class MyHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length)

        # Decode URL path and split into command parts
        raw_path = urllib.parse.unquote(self.path.lstrip("/"))
        cmd_parts = shlex.split(raw_path)

        # Normalize first element to basename (safe fallback)
        cmd_parts[0] = os.path.basename(cmd_parts[0])

        # Enforce whitelist if one is configured
        if ALLOWED and cmd_parts[0] not in ALLOWED:
            print(f"Rejected (not whitelisted): {cmd_parts[0]}")
            self.send_response(403)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.end_headers()
            self.wfile.write(f"Error: command '{cmd_parts[0]}' is not allowed.\n".encode())
            return

        print("Executing:", cmd_parts)

        try:
            process = subprocess.Popen(
                cmd_parts,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )

            # Write stdin data and close it so the process sees EOF
            if body:
                process.stdin.write(body)
            process.stdin.close()

            self.send_response(200)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.send_header("Transfer-Encoding", "chunked")
            self.end_headers()

            # Merge stdout and stderr into one queue via reader threads,
            # so both streams are forwarded live and neither can block the other
            line_queue = queue.Queue()

            def reader(stream, prefix):
                for line in stream:
                    line_queue.put(prefix + line if prefix else line)
                line_queue.put(None)  # sentinel: this stream is done

            t_out = threading.Thread(target=reader, args=(process.stdout, b""))
            t_err = threading.Thread(target=reader, args=(process.stderr, b"[stderr] "))
            t_out.start()
            t_err.start()

            done_count = 0
            while done_count < 2:
                chunk = line_queue.get()
                if chunk is None:
                    done_count += 1
                    continue
                self.wfile.write(f"{len(chunk):X}\r\n".encode())
                self.wfile.write(chunk)
                self.wfile.write(b"\r\n")
                self.wfile.flush()

            t_out.join()
            t_err.join()
            process.wait()

            # Terminate chunked transfer
            self.wfile.write(b"0\r\n\r\n")
            self.wfile.flush()

        except FileNotFoundError:
            self.send_response(200)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.end_headers()
            self.wfile.write(f"Error: command not found: {cmd_parts[0]}\n".encode())

    def log_message(self, format, *args):
        print(f"[{self.address_string()}] {format % args}")

if __name__ == "__main__":
    server = HTTPServer(("0.0.0.0", 8000), MyHandler)

    if TLS_CERT and TLS_KEY:
        ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        ctx.load_cert_chain(certfile=TLS_CERT, keyfile=TLS_KEY)
        server.socket = ctx.wrap_socket(server.socket, server_side=True)
        print(f"Serving HTTPS on 0.0.0.0:8000 (cert: {TLS_CERT})")
    else:
        print("Serving HTTP on 0.0.0.0:8000 (set REMOTE_EXEC_TLS_CERT and "
              "REMOTE_EXEC_TLS_KEY to enable HTTPS)")

    server.serve_forever()
