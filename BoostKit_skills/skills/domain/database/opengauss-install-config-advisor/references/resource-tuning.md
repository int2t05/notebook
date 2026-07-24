# Resource-Aware Tuning

Use this reference after openGauss is installed and running. Only tune from confirmed resources and user goals.

## Required Inputs

Ask for:

- CPU cores.
- Total memory.
- Disk free space for data/logs.
- Storage type if known: HDD, SSD, NVMe.
- Install method: container or native package.
- Container memory/CPU limits if containerized.
- Main goal: learning, local application testing, small persistent use, or performance exploration.

If the user has not provided enough data, ask for:

```bash
lscpu
free -h
df -h
docker stats --no-stream
docker inspect <container-name>
```

Use Docker commands only when the user is running openGauss in a container.

## Tuning Principles

- Keep suggestions conservative for ordinary users.
- Explain why each setting is suggested.
- Say whether a change needs reload or restart.
- Provide verification steps.
- Do not pretend workload-specific optimal values are known.
- Prefer using openGauss tools when available.

If the native installation includes `gs_check` or `gs_checkos`, suggest running them before manual OS tuning.

If the user asks for performance tuning beyond lightweight use, suggest `gs_perfconfig suggest` or the openGauss performance tuning guide.

## Resource Profiles

### Low Resource: Around 2C4G

Use for learning and light tests.

Advice:

- Keep connection count modest.
- Avoid large memory settings.
- Avoid large parallel workloads.
- Warn that complex queries or high concurrency may be slow or fail from memory pressure.
- Prefer container only if the container has enough memory and persistent volume.

Starting points to discuss:

- Prefer defaults unless the user has a concrete symptom.
- Keep `max_connections` low enough for expected local clients only.
- Avoid increasing `work_mem` unless a query needs it and concurrency is low.
- Avoid large `shared_buffers` values; leave room for OS cache and the container/runtime if applicable.
- Keep logging retention modest if disk is limited.

Avoid:

- Running performance benchmarks as if this were a production-like host.
- Enabling broad remote access for convenience.
- Applying OS-level tuning without understanding privilege and restart impact.

### Moderate Resource: Around 4C8G

Use for local application testing and light persistent use.

Advice:

- Moderate connection and memory settings may be reasonable.
- Keep enough memory for the OS and client tools.
- Avoid assuming production concurrency.
- Watch disk growth from data, WAL, and logs.

Starting points to discuss:

- Consider a modest `max_connections` only if the application needs multiple concurrent sessions.
- Consider `work_mem` only in relation to query complexity and concurrent queries.
- Consider `shared_buffers` only as a conservative fraction of memory after reserving memory for OS, clients, and containers.
- Check disk space for data, WAL, and logs before increasing workload volume.
- Run `gs_check` or `gs_checkos` when available before OS-level changes.

Avoid:

- Treating 4C8G as enough for high-concurrency or production workloads by default.
- Raising multiple memory-related parameters at the same time without verification.

### Comfortable Local Resource: 8C16G Or Higher

Use for stronger local experiments.

Advice:

- More active connections and memory may be reasonable, still conservatively.
- Place data on SSD/NVMe if available.
- Consider separating heavy test data from the system disk.
- Use openGauss tuning tools before manual deep parameter changes.

Starting points to discuss:

- More active connections may be reasonable, but still tie `max_connections` to expected clients.
- `work_mem` can be discussed for query-heavy tests, but explain per-operation/per-query memory risk.
- `shared_buffers` can be discussed as a larger cache, but avoid universal values.
- Prefer faster storage for data and test datasets.
- Consider `gs_perfconfig` suggestion/report mode before applying tuning.

Avoid:

- Presenting local-resource settings as production best practices.
- Applying `gs_perfconfig --apply` without explicit user consent and restart awareness.

## Suggested Output Shape

Use this structure:

```text
Resource summary:
- CPU:
- Memory:
- Disk:
- Runtime:
- Goal:

Recommendations:
1. ...
   Why:
   How:
   Reload/restart:
   Verify:

Not recommended:
- ...
```

## Parameters To Discuss Carefully

Discuss these only after confirming the user's install method and resource profile:

- `max_connections`: increasing it consumes more memory and should match expected clients.
- `work_mem`: depends on query complexity and concurrency; do not set high values blindly.
- `shared_buffers`: memory-sensitive; leave conservative unless there is enough RAM and a reason to tune.
- Logging and retention settings: useful when disk is tight.
- `listen_addresses` and `pg_hba.conf`: security-sensitive; not performance tuning.

Avoid giving exact universal values. If you provide a value, label it as a starting point and explain that it must be validated against the user's workload.
