# Safety Gates

Pause and ask for explicit confirmation before:

- Installing or upgrading system packages.
- Replacing drivers, CUDA, cuDNN, Java, Go, Python, Docker, or other host-level runtimes.
- Running destructive package-manager cleanup.
- Entering credentials, tokens, private registry settings, or SSH keys.
- Accepting a new or changed SSH host key, unlocking a private key, entering an SSH password, or handling a sudo password on a remote host.
- Uploading code, cloning remotely, or overwriting a remote project directory.
- Choosing between ambiguous project types or Java build tools.
- Continuing after tests fail for reasons that do not look environment-only.

Prefer:

- Dry-run plans before execution.
- Project-local isolation over host-wide changes.
- Append-only notes and logs over hidden state.
- Redacted output whenever credentials may appear.
- SSH commands that use an already-confirmed host and existing remote project path.
