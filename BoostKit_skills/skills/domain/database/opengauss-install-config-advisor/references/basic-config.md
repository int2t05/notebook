# Basic Configuration

Use this reference after openGauss is installed or when the user asks about connection and persistence settings.

## Required vs Recommended vs Risky

Required:

- Valid password and account setup.
- Data directory or container volume that persists.
- A port that is not already occupied.
- Local connection verification.

Recommended:

- Keep local-only access unless remote access is required.
- Put data and logs on storage with enough free space.
- Keep a record of install path, data path, port, and runtime user.
- Use openGauss tools such as `gs_check` or `gs_checkos` when available.

Risky:

- `listen_addresses='*'`.
- Broad `pg_hba.conf` entries such as `0.0.0.0/0`.
- Opening firewall ports to untrusted networks.
- Weak passwords.
- Running without persistent volume in a container.

## Port Checks

Use:

```bash
ss -lntp | grep ':5432'
```

If port `5432` is occupied, choose another port and document it.

## Local Connection

After startup, verify local connectivity. The exact command depends on the install method and user/database names. Use placeholders when unknown:

```bash
gsql -d postgres -p <port>
```

If `gsql` is not in `PATH`, ask the user to locate the openGauss `bin` directory or use the full path.

## Remote Access

Only configure remote access when the user asks for it.

Before changing configuration, ask:

- Which client IP or subnet needs access?
- Is this a trusted private network?
- Which port should be exposed?
- Is firewall access required?

Prefer narrow settings:

- Use a specific server IP instead of `*` for `listen_addresses` when possible.
- Use a specific client IP or small CIDR in `pg_hba.conf`.
- Avoid `0.0.0.0/0` unless the user explicitly accepts the risk.

After changing `postgresql.conf` or `pg_hba.conf`, tell the user whether reload or restart is needed. If unsure, recommend checking the parameter context in the openGauss docs or using the documented openGauss reload/restart command for their install method.

## Container Persistence

For containers, confirm that the user used a host volume or named volume. Without it, removing the container may remove database data.

Ask for:

```bash
docker inspect <container-name>
docker ps --filter name=<container-name>
```

Check that a host path or named volume is mounted to the container's data path according to the image documentation.

## Firewall

Only open firewall rules for remote access. Prefer limiting source IPs at the firewall and in `pg_hba.conf`.

Do not provide a broad firewall open command without warning about exposure.
