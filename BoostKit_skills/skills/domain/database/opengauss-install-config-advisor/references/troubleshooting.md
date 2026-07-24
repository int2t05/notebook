# Troubleshooting

Use this reference when installation, startup, or connection fails.

## Method

Ask for the smallest useful next output:

- The exact command run.
- The exact error message.
- The install method: container or native package.
- The target openGauss version if known.
- Relevant logs, limited to the last 50-100 lines.

Do not ask for broad logs before checking the obvious next cause.

## Common Checks

### Unsupported OS Or Architecture

Ask for:

```bash
cat /etc/os-release
uname -m
```

If native package compatibility is unclear, recommend confirming the matching official package or switching to a compatible container image.

### Missing Dependencies

Ask for the failed command and package manager output.

Do not invent dependency package names for every OS. Identify the missing library or command from the error, then map it to the user's OS package manager.

### Permission Denied

Ask for:

```bash
id
ls -ld <install-dir> <data-dir> <log-dir>
```

Check ownership and write permissions for the runtime user.

### Port Already In Use

Ask for:

```bash
ss -lntp | grep ':<port>'
```

Recommend choosing another port or stopping the conflicting service.

### Container Starts Then Exits

Ask for:

```bash
docker ps -a --filter name=<container-name>
docker logs --tail 100 <container-name>
docker inspect <container-name>
```

Common causes:

- Password policy failure.
- Wrong image architecture.
- Unwritable data volume.
- Port conflict.
- Insufficient memory.
- Incorrect environment variable names for the chosen image.

### Cannot Connect Locally

Ask for:

```bash
ss -lntp | grep '<port>'
ps -ef | grep gaussdb
gsql --version
```

For containers:

```bash
docker ps
docker port <container-name>
docker logs --tail 100 <container-name>
```

Check server status, port mapping, and whether the client is connecting to the right host and port.

### Cannot Connect Remotely

Check in order:

1. Server is listening on the expected address and port.
2. `listen_addresses` allows the target server interface.
3. `pg_hba.conf` allows the specific client IP or subnet.
4. Firewall allows the port from the client IP.
5. Client uses the correct host, port, database, and user.

Avoid recommending `0.0.0.0/0` unless the user explicitly accepts the risk.

### Configuration Changed But Not Applied

Ask what file changed and how the user applied it.

Explain that some settings can be reloaded while others require restart. When unsure, guide the user to use the documented openGauss reload/restart command for their install method.

## Response Pattern

Use:

```text
Likely cause:
Evidence:
Next check:
Command:
Expected result:
If different:
```
