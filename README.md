# remote-exec-server
Lightweight HTTP server + client that forwards stdin to a remote process and returns stdout. Inspired by the busybox style: one client script, multiple command names via symlinks. Supports dynamic commands like gp, python, node, etc. with normalization for safety.
