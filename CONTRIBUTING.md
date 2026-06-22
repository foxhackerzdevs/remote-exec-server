# Contributing Guidelines

Thank you for considering contributing to **Remote Exec Server & Client**!  
This project is lightweight by design, so contributions should keep things simple, secure, and easy to maintain.

---

## 📖 Documentation Guidelines
- **Headings**: Avoid emojis in section headers. GitHub generates anchor links from the full heading text, and emojis can break Table of Contents navigation.
- **Badges**: Place all badges (license, Python version, stars, forks, release, downloads) together at the top of the README for consistency.
- **Commit Messages**: Use [Conventional Commits](https://www.conventionalcommits.org/) — e.g., `docs: fix Quick Start TOC link`.
- **Release Notes**: Every doc change that affects navigation or visibility should be tagged with a patch version (e.g., `v1.1.3`).

---

## 🔐 Security Guidelines
- **Authentication**: Contributions adding new features should consider API keys, bearer tokens, or mutual TLS.
- **Isolation**: Prefer Docker containers or restricted user accounts for execution.
- **Encryption**: Use HTTPS/TLS whenever traffic crosses untrusted networks.
- **Whitelisting**: Commands should be explicitly allowed via a whitelist.

---

## 🛠️ Development Guidelines
- Keep dependencies minimal (Python standard library preferred).
- Write clear, small commits — one logical change per commit.
- Add tests for new features where possible.
- Document new features in the README or inline comments.

---

## 🚀 Contribution Flow
1. Fork the repository.
2. Create a feature branch (`git checkout -b feature/my-change`).
3. Make your changes and commit (`git commit -m "feat: add TLS support"`).
4. Push to your fork and open a Pull Request.
5. Ensure your PR description explains the change clearly.

---

By following these guidelines, we keep the project lightweight, secure, and contributor‑friendly.

