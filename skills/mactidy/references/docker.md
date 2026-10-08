# Docker cleanup on macOS

Use this reference when Docker, Compose, or BuildKit cleanup is requested.
Include the findings in the [visual review](visual-review.md). For a general
Docker cleanup request, show the candidates and ask which exact resources to
remove. Honor an already authorized concrete operation or exact batch without
repeating the permission request. Retain uncertain data and report why it was
excluded; unreferenced volume counts are not proof of safe deletion.

## Inventory and context

Record host free bytes with `df -k /System/Volumes/Data`, then inspect:

```bash
docker context show
docker context inspect CONTEXT
docker compose ls --all --format json
docker ps -a --no-trunc --format '{{json .}}'
docker system df
docker volume ls
docker buildx ls
```

Confirm that the endpoint belongs to the local Mac, such as Docker Desktop or
OrbStack. Do not prune a remote daemon under a request to clean this Mac. Pin the
verified context for subsequent commands; stop if its endpoint changes.

Inspect exact containers and volumes. Record IDs, state, Compose project and
config-file labels, working directories, port bindings, bind mounts, volume
references, and writable-layer purpose. Avoid printing container environment
variables or unsanitized process commands: they may contain credentials.

Count volume references from **all** containers, including stopped containers.
Docker's `dangling=true` or zero links means unreferenced, not disposable.

## Stop unused workloads

Establish purpose and current dependencies using the owning project, live host
processes, open files, TCP clients, container connections, and relevant logs.
Recent tasks, active tests, database clients, and build requests protect a
workload. Age, an absent worktree, a test-like name, or a single idle connection
snapshot alone is insufficient.

For a proven abandoned Compose project with its original configuration and
required settings available, use the exact project and config files:

```bash
docker --context CONTEXT compose -p PROJECT -f /exact/compose.yaml stop
```

Do not invent replacement configuration if files are missing. Instead, verify
the original project labels and full container IDs, then stop that exact set:

```bash
docker --context CONTEXT stop --time 30 CONTAINER_ID
```

`compose down` also removes project containers and networks; use it only when
their writable layers are disposable. Omit `-v` and `--remove-orphans` unless
those additional exact resources were reviewed and authorized.

For BuildKit, match containers to the builder registry and check active build
processes and cache records with `buildctl du` where available. Registered
builders should be stopped or removed through `docker buildx`. An unregistered
builder container can be stopped by its exact ID after proving no build uses it.
Its `/var/lib/buildkit` volume is reproducible cache only after that ownership
and lack of active builds are established.

## Prune and volumes

Before `system prune`, review stopped containers: their writable layers may
hold unique data. If an uncertain stopped container would be included, use
exact resource removal or filters that exclude it instead of a blanket prune.
Check the installed command's help for supported filters and volume semantics.

The ordinary requested system prune is:

```bash
docker --context CONTEXT system prune --force
```

This removes stopped containers, unused networks, dangling images, and eligible
build cache. It does not remove volumes without `--volumes`. Do not silently
add `--all`, `--volumes`, or `volume prune --all`; each broadens the batch.

Classify unreferenced volumes separately:

- Empty volumes: inspect their contents read-only and verify they are empty.
- Reproducible caches: confirm the creator and cache layout, and check that no
  container, active build, or retained project depends on them.
- Databases and application state: retain them unless fixtures/rebuildability,
  a verified backup, or explicit authorization to discard those exact data is
  established. Named and anonymous volumes receive the same protection.

A temporary helper using an existing image, `--pull=never`, `--network none`,
`--read-only`, and read-only volume mounts can inspect contents. Use `--rm`,
ensure the image does not declare extra persistent volumes, and record helper
names so an interrupted probe can be identified. Do not start a database on an
unknown volume merely to inspect it; initialization or recovery can write data.

For each disposable volume, immediately re-check its driver, labels, creation
identity, all-container references, and the decisive content or ownership
evidence. Remove only exact names:

```bash
docker --context CONTEXT volume rm EXACT_VOLUME_NAME
```

Never force volume removal. If a resource becomes referenced, a new build
appears, or any identity/evidence changes, stop and reclassify that target.

## Verify

Compare before/after container IDs and volume names. Confirm retained services
and volumes remain, helpers have exited, and intended ports have closed. Re-run
`docker compose ls --all`, `docker system df`, and a lightweight Docker health
check. Measure `df -k /System/Volumes/Data` again.

Report Docker's reclaimed logical bytes separately from the change in macOS
free bytes: VM disks, sparse files, APFS sharing, and concurrent development can
make them differ. Report stopped workloads, deleted caches/volumes, preserved
uncertain databases, and any incomplete checks. Do not manually delete Docker
or OrbStack VM disk files or shut down the VM while retained services run.
