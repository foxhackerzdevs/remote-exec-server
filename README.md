# Remote Exec Server & Client

A lightweight HTTP server and client pair that lets you run commands on a remote machine as if they were local. Inspired by the BusyBox model: a single client script invoked under multiple names via symlinks, each forwarding to a different command on the server.

The original use case: run `gp` (PARI/GP) on a machine that has it installed, from a machine that doesn't.

---

## How It Works

- **`client.py`** reads stdin, encodes the invoked command name and arguments into the URL path, and POSTs to the server. The response (stdout of the remote command) is printed locally.
- **`server.py`** receives the request, decodes the command name (normalized to basename to prevent path traversal), executes it via `subprocess.run` with the POST body as stdin, and returns stdout.
- **Symlinks** allow a single `client.py` to behave as `gp`, `node`, `python`, or any other command — whichever name it was invoked under is forwarded to the server.

---

## Installation

### Server (the machine running the commands)

1. Copy `server.py` to the server machine.
2. Run it:
   ```bash
   python server.py
   ```
   The server listens on `0.0.0.0:8000` by default.

### Client (your local machine)

1. Edit `client.py` and set `host` to your server's IP and port:
   ```python
   host = "192.168.56.1:8000"
   ```

2. Make it executable and place it in your PATH:
   ```bash
   chmod +x client.py
   cp client.py ~/bin/
   ```

3. Create symlinks for each command you want to forward:
   ```bash
   ln -s ~/bin/client.py ~/bin/gp
   ln -s ~/bin/client.py ~/bin/node
   ```

   Do not overwrite existing local binaries you still need.

---

## Usage

```bash
# Run PARI/GP on the server
echo "print(nextprime(100))" | gp -q

# Pipe a script to the server's Python
echo "print('hello')" | python

# Use with pari-gp-scripts
./gilbreath.sh 100
./mobius.sh 1000
```

The client forwards stdin and argv to the server, which executes the command and streams stdout back.

---

## Security

This server executes arbitrary commands. **Never expose it to untrusted networks.**

- Run it on a private or host-only network interface only
- Add a command whitelist in `server.py` to restrict what can be executed:
  ```python
  ALLOWED = {"gp", "node", "python"}
  if cmd_parts[0] not in ALLOWED:
      output = f"Error: command '{cmd_parts[0]}' is not allowed."
      # send response and return
  ```
- Never run the server with elevated privileges

---

## License

MIT — see [LICENSE](LICENSE) for details.
