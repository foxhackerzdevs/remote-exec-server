<div align="center">

# 🚀 Remote Exec Server & Client

![License](https://img.shields.io/badge/License-MIT-blue.svg)
![Python](https://img.shields.io/badge/Python-3.8%2B-green.svg)
![GitHub stars](https://img.shields.io/github/stars/foxhackerzdevs/remote-exec-server?style=social)
![GitHub forks](https://img.shields.io/github/forks/foxhackerzdevs/remote-exec-server?style=social)

**Lightweight Python-based remote command execution system**  
Inspired by the BusyBox model: one client script invoked under multiple names via symlinks, enabling remote execution of different programs transparently.  

[Overview](#overview) • [Installation](#installation) • [Usage](#usage) • [Security Considerations](#security-considerations) • [License](#license)

</div>

---

## 🌟 Overview

This project provides a simple yet powerful way to execute commands on a remote machine through a basic HTTP interface. The core idea is to have a server listening for commands and a client that forwards local command invocations and standard input to this server.

**How it works:**

- **Client (`client.py`):**
  1. Detects the command name it was invoked as (e.g., `gp`, `python`, `node`).
  2. Reads command-line arguments and standard input.
  3. Sends an HTTP POST request to the remote server containing the command and its arguments, along with the stdin data.

- **Server (`server.py`):**
  1. Receives the HTTP request.
  2. Decodes the command and arguments from the URL path.
  3. Executes the command locally using Python's `subprocess.run()`.
  4. Captures stdout and stderr.
  5. Returns the captured stdout (or error message) back to the client.

**Example use cases:**

- Running PARI/GP remotely
- Executing scripts on a dedicated compute machine
- Accessing tools installed only on a server
- Thin-client command forwarding

---

## 🏗️ Architecture

```text
┌─────────────┐
│   Client    │
│  (symlink)  │
└──────┬──────┘
       │ HTTP POST
       ▼
┌─────────────┐
│   Server    │
│ server.py   │
└──────┬──────┘
       │
       ▼
┌─────────────┐
│ subprocess  │
│ execution   │
└─────────────┘
```

---

## ✨ Features

- **Simple HTTP protocol** — straightforward POST request to send commands
- **Stdin forwarding** — supports piping input to the remote command
- **Argument support** — passes command-line arguments to the remote process
- **Versatile execution** — works with any executable available on the server
- **BusyBox-style symlinks** — a single client script emulates multiple commands
- **Minimal dependencies** — relies only on the Python standard library

---

## 💻 Tech Stack

- **Language:** Python 3.8+
- **Libraries:** Python standard library only (`http.server`, `subprocess`, `urllib`, `shlex`, `os`)

---

## 📋 Requirements

- Python 3.8+
- Network connectivity between client and server

No third-party packages required.

---

## ⬇️ Installation

### Server Setup

1. Copy `server.py` to the machine that will execute commands.
2. Start the server:
   ```bash
   python server.py
   ```
   The server listens on `0.0.0.0:8000` by default.

### Client Setup

1. Edit `client.py` to set the server address:
   ```python
   host = "SERVER_IP:8000"
   ```

2. Make it executable and place it in your PATH:
   ```bash
   chmod +x client.py
   cp client.py ~/bin/
   ```

3. Create symlinks for each command to forward:
   ```bash
   ln -s ~/bin/client.py ~/bin/gp
   ln -s ~/bin/client.py ~/bin/node
   ```

   When invoked through a symlink, the client forwards that command name to the server.

---

## ▶️ Usage

```bash
# With piped input
echo "input data" | command_name [args]

# Without piped input
command_name [args]
```

Where `command_name` is one of the symlinks pointing to `client.py`.

---

## 💡 Examples

### Run PARI/GP remotely

```bash
echo "print(nextprime(100))" | gp -q
```

### Run a remote Python command

```bash
echo "print('Hello World')" | python
```

### Pass arguments to a remote command

```bash
echo "hello" | python script.py some_arg another_arg
```

### Run remote Node.js

```bash
echo "console.log('hello from node')" | node
```

---

## ⚙️ Configuration

### Client

Change the server address:
```python
host = "YOUR_SERVER_IP:8000"
```

For TLS, replace `http.client.HTTPConnection` with `http.client.HTTPSConnection`. The server must also be configured for TLS.

### Server

Restrict to localhost only:
```python
server = HTTPServer(("127.0.0.1", 8000), MyHandler)
```

---

## 🛡️ Security Considerations

⚠️ **This server executes arbitrary commands received over HTTP. Never expose it to untrusted networks.**

### Command whitelist

Add a whitelist to `server.py` to restrict allowed commands:

```python
ALLOWED = {"gp", "python", "node"}

if cmd_parts[0] not in ALLOWED:
    output = f"Command not allowed: {cmd_parts[0]}"
    # send error response and return
```

### Network restrictions

- Use a VPN, SSH tunnel, or host-only network
- Apply firewall rules to restrict access to trusted IPs only
- Never expose the server port directly to the internet

### Additional measures

- Add API key or bearer token authentication
- Never run with elevated privileges
- Consider sandboxing via Docker, chroot, or a restricted user account
- Use HTTPS when transmitting over any untrusted network

---

## 🛠️ Troubleshooting

**Command not found** — ensure the executable exists on the server:
```bash
which gp
which python
which node
```

**Connection refused** — confirm `server.py` is running and the `host` in `client.py` matches the server's IP and port.

**No output returned** — check server logs; verify the command writes to stdout and not exclusively to stderr.

**Wrong host** — double-check the `host` variable in `client.py`.

---

## 📂 Project Structure

```text
.
├── client.py     # Client script for sending commands
├── server.py     # Server script for executing commands
├── README.md     # Documentation
└── LICENSE       # MIT License
```

---

## 🚀 Future Improvements

- HTTPS / TLS support
- Authentication (API keys, bearer tokens, mutual TLS)
- Command whitelisting built-in
- Streaming output
- Async request handling
- File transfer
- Rate limiting and audit logging
- Docker deployment

---

## 🤝 Contributing

Contributions are welcome. Feel free to fork the repository, open an issue, or submit a pull request.

---

## 📜 License

MIT — see [LICENSE](LICENSE) for details.
