# 🚀 Remote Exec Server & Client

A lightweight Python-based remote command execution system. This project allows you to execute commands on a remote server by making HTTP requests from a client script.

Inspired by the BusyBox model, a single client script can be invoked under multiple names via symlinks, enabling the remote execution of different programs transparently.

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Requirements](#requirements)
- [Installation](#installation)
  - [Server Setup](#server-setup)
  - [Client Setup](#client-setup)
- [Usage](#usage)
- [Examples](#examples)
- [Configuration](#configuration)
- [Security Considerations](#security-considerations)
- [Troubleshooting](#troubleshooting)
- [Project Structure](#project-structure)
- [Future Improvements](#future-improvements)
- [Contributing](#contributing)
- [License](#license)
- [Footer](#footer)

---

## 🌟 Overview

This project provides a simple yet powerful way to execute commands on a remote machine through a basic HTTP interface. The core idea is to have a server listening for commands and a client that forwards local command invocations and standard input to this server.

**How it works:**

- **Client:**
  1. Detects the command name it was invoked as (e.g., `gp`, `python`, `node`).
  2. Reads command-line arguments and standard input.
  3. Sends an HTTP POST request to the remote server containing the command and its arguments, along with the stdin data.

- **Server (`server.py`):**
  1. Receives the HTTP request.
  2. Decodes the command and arguments from the URL path.
  3. Executes the command locally using Python's `subprocess.run()`.
  4. Captures stdout and stderr.
  5. Returns the captured stdout (or error message) back to the client.

This setup is particularly useful for running software remotely from systems where the software is not installed, such as executing PARI/GP on a machine that doesn't have it locally.

**Example Use Cases:**

- Running PARI/GP remotely.
- Executing scripts on a dedicated compute machine.
- Accessing tools installed only on a server.
- Thin-client command forwarding.

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

- **Simple HTTP Protocol:** Uses a straightforward POST request to send commands.
- **Stdin Forwarding:** Supports piping input to the remote command.
- **Argument Support:** Passes command-line arguments to the remote process.
- **Versatile Execution:** Works with any executable available on the server.
- **BusyBox-Style Symlinks:** A single client script can emulate multiple commands via symlinks.
- **Minimal Dependencies:** Relies only on the Python standard library, making setup easy.

---

## 💻 Tech Stack

- **Languages:** Python
- **Frameworks/Libraries:** Python Standard Library (http.server, subprocess, urllib, shlex, os)

---

## 📋 Requirements

- **Python:** Version 3.8+ required.
- **Network:** Stable network connectivity between the client and server machines.

No third-party Python packages are required for this project.

---

## ⬇️ Installation

### Server Setup 🖥️

1.  **Copy the `server.py` script** to the machine that will be responsible for executing commands.
2.  **Start the server** by running the script:
    ```bash
    python server.py
    ```
    By default, the server listens on `0.0.0.0:8000`.

### Client Setup 💻

1.  **Edit the `client.py` script** to specify the server's address:
    ```python
    host = "SERVER_IP:8000"
    ```
    Replace `SERVER_IP` with the actual IP address of your server.

2.  **Make the client script executable:**
    ```bash
    chmod +x client.py
    ```

3.  **Install the client script** in your system's PATH for easy access (e.g., in `~/bin/`):
    ```bash
    cp client.py ~/bin/
    ```

#### Creating Command Symlinks 🔗

To leverage the BusyBox-style functionality, create symbolic links for commands you want to execute remotely. For example, to enable remote execution of `gp`, `python`, and `node`:

```bash
# Assuming ~/bin/ is in your PATH
ln -s ~/bin/client.py ~/bin/gp
ln -s ~/bin/client.py ~/bin/python
ln -s ~/bin/client.py ~/bin/node
```

Now, when you invoke `gp`, `python`, or `node` in your terminal, the `client.py` script will intercept it and forward the request to the server, using the symlink name as the command to execute.

---

## ▶️ Usage

Once the server is running and the client is set up with symlinks, you can execute commands remotely. The general form is:

```bash
# With piped input
echo "input data" | command_name [args] 

# Without piped input
command_name [args]
```

Where `command_name` is one of the symlinks you created (e.g., `gp`, `python`, `node`).

---

## 💡 Examples

### Run PARI/GP Remotely 🔢

Execute a PARI/GP command on the server:

```bash
echo "print(nextprime(100))" | gp -q
```

### Run Remote Python Script 🐍

Execute a Python command or script on the server:

```bash
echo "print('Hello World')" | python
```

### Pass Arguments to Remote Command ⚙️

Execute a Python script with arguments on the server:

```bash
echo "hello" | python script.py some_arg another_arg
```

### Run Remote Node.js 🚀

Execute a Node.js command on the server:

```bash
echo "console.log('hello from node')" | node
```

---

## ⚙️ Configuration

### Client Configuration 🔧

-   **Server Address:** Modify the `host` variable in `client.py` to point to your server's IP address and port:
    ```python
    host = "YOUR_SERVER_IP:8000"
    ```

-   **TLS/HTTPS:** For secure connections, replace `http.client.HTTPConnection` with `http.client.HTTPSConnection` in `client.py`. Note that the server must also be configured for TLS.

### Server Configuration 🔧

-   **Bind Address:** The server defaults to listening on all interfaces (`0.0.0.0`) and port `8000`:
    ```python
    server = HTTPServer(("0.0.0.0", 8000), MyHandler)
    ```

-   **Localhost Only:** To restrict the server to only accept connections from the local machine, change the bind address to `127.0.0.1`:
    ```python
    server = HTTPServer(("127.0.0.1", 8000), MyHandler)
    ```

---

## 🛡️ Security Considerations

⚠️ **Crucial Warning:** This project executes arbitrary commands received over HTTP. Running the server on a public or untrusted network is **extremely dangerous** and can lead to severe security breaches.

### Recommended Protections:

1.  **Command Whitelist:** Implement a strict whitelist of allowed commands on the server to prevent execution of unintended or malicious programs. The `server.py` code has a commented-out example:
    ```python
    # ALLOWED = {"gp", "python", "node"}
    # if cmd_parts[0] not in ALLOWED:
    #     output = f"Command not allowed: {cmd_parts[0]}"
    #     # Handle error appropriately (e.g., send error response)
    #     return
    ```

2.  **Network Restrictions:** Always use network-level security measures:
    *   **VPN Access:** Ensure clients connect via a Virtual Private Network.
    *   **SSH Tunnels:** Forward the server port securely over an SSH tunnel.
    *   **Host-Only Networks:** Use private, isolated network configurations.
    *   **Firewall Rules:** Restrict access to the server port only from trusted IP addresses.

    **Never expose the server directly to the Internet.**

3.  **TLS Encryption:** Use HTTPS (by configuring both client and server for `HTTPSConnection`) when transmitting commands over any untrusted network, even if internal.

4.  **Authentication:** For enhanced security, consider implementing:
    *   API Keys
    *   Bearer Tokens
    *   Mutual TLS (mTLS)
    *   IP Allowlisting on the server-side

5.  **Sandbox Execution:** For maximum security, run commands within isolated environments:
    *   Docker containers
    *   Virtual machines
    *   `chroot` environments
    *   Dedicated, restricted user accounts

---

## 🛠️ Troubleshooting

### Command Not Found Error ❓

**Symptom:** The server returns `Error: command not found: <command_name>`.

**Solution:** Ensure the executable (`gp`, `python`, `node`, etc.) is installed and accessible in the server's PATH.

```bash
# On the server:
which python
which gp
which node
```

### Connection Refused Error ❌

**Symptom:** The client fails to connect, showing "Connection Refused".

**Solution:** Verify that the server is running and listening on the correct IP address and port.

```bash
# On the server:
python server.py
```

Check that the `host` variable in `client.py` matches the server's IP and port.

### No Output Returned 🤷

**Symptom:** The client runs but returns no output or an empty response.

**Solutions:**

*   Check the server logs for any errors during command execution.
*   Verify that the command has the necessary file permissions to execute on the server.
*   Ensure the command writes its output to `stdout` and not exclusively to `stderr`.

### Incorrect Host Address 📍

**Symptom:** Connection errors or the wrong server being contacted.

**Solution:** Double-check and correct the `host` variable in `client.py` to accurately reflect the server's IP address and port:

```python
host = "SERVER_IP:8000"
```

---

## 📂 Project Structure

The project has a simple and straightforward structure:

```text
.                       <-- Project Root
├── client.py           # The client script for sending commands
├── server.py           # The server script for executing commands
└── README.md           # This documentation file
└── LICENSE             # Project License file
```

---

## 🚀 Future Improvements

Potential enhancements for this project include:

*   **HTTPS Support:** Implement TLS for secure communication.
*   **Authentication:** Add mechanisms like API keys or tokens.
*   **Command Whitelisting:** Enhance security by strictly defining allowed commands.
*   **Streaming Output:** Support real-time streaming of command output.
*   **Async Request Handling:** Improve server performance with asynchronous operations.
*   **File Transfer:** Add functionality to upload/download files.
*   **Rate Limiting:** Protect the server from abuse.
*   **Logging and Auditing:** Implement comprehensive logging for security and debugging.
*   **Docker Deployment:** Provide Dockerfiles for easier deployment.

---

## 🤝 Contributing

Contributions are welcome! Please feel free to:

*   Fork the repository.
*   Open an issue to discuss potential changes or report bugs.
*   Submit a pull request with your improvements.

---

## 📜 License

This project is licensed under the **MIT License**. 

You are free to use, modify, and distribute this software under the terms of the MIT License.

---

## 🔗 Footer

| Repository | Author | Contact |
|---|---|---|
| [remote-exec-server](https://github.com/foxhackerzdevs/remote-exec-server) | [foxhackerzdevs](https://github.com/foxhackerzdevs) | [foxhackerzdevs@gmail.com](mailto:foxhackerzdevs@gmail.com) |

<p align="center">
  Enjoying this project? Give it a :star: on GitHub!
  <br/>
  <a href="https://github.com/foxhackerzdevs/remote-exec-server/fork" target="_blank">
    <img src="https://img.shields.io/github/forks/foxhackerzdevs/remote-exec-server?style=social" alt="Fork Repository">
  </a>
  <a href="https://github.com/foxhackerzdevs/remote-exec-server/stargazers" target="_blank">
    <img src="https://img.shields.io/github/stars/foxhackerzdevs/remote-exec-server?style=social" alt="Star Repository">
  </a>
  <br/>
  <a href="https://github.com/foxhackerzdevs/remote-exec-server/issues" target="_blank">
    <img src="https://img.shields.io/github/issues/foxhackerzdevs/remote-exec-server" alt="Open Issues">
  </a>
</p>


---
**<p align="center">Generated by [ReadmeCodeGen](https://www.readmecodegen.com/)</p>**