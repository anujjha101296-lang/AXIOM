# Known Limitations

- **Scalability**: All data stores currently use SQLite.
- **LLM Context Limits**: The system lacks an explicit context-window truncation mechanism.
- **Security Sandbox**: `SecureSandbox` protects against basic Python `os` and `sys` injections but is not a containerized hypervisor.
- **Authentication**: Uses basic JWT Bearer tokens; no external OAuth providers implemented.
