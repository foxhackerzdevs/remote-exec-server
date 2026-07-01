#!/usr/bin/env python3
from http.server import BaseHTTPRequestHandler, HTTPServer
import subprocess, urllib.parse, shlex, os, threading, queue

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
    print("Serving on 0.0.0.0:8000")
    server.serve_forever()

