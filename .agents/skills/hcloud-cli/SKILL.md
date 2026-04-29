---
name: hcloud-cli
description: >-
  Use the Hetzner Cloud CLI (hcloud) to manage cloud resources from the
  terminal. Use when the user wants to create, list, describe, update, or
  delete servers, firewalls, networks, volumes, floating IPs, SSH keys,
  DNS zones, load balancers, images, placement groups, primary IPs,
  storage boxes, or certificates on Hetzner Cloud. Also use when
  installing/setting up hcloud, configuring contexts and authentication,
  querying datacenters/locations/server-types, using output options
  (JSON/YAML/template/table), or scripting cloud infrastructure.
license: MIT
metadata:
  author: iAziz786
  version: "1.0"
---

# Hetzner Cloud CLI (hcloud)

## When To Use

- User mentions "hcloud", "Hetzner Cloud CLI", "Hetzner" + server/cloud
- Creating, listing, describing, updating, deleting any Hetzner Cloud resource
- Setting up or authenticating Hetzner Cloud CLI
- Managing DNS zones and records on Hetzner Cloud
- Scripting or automating Hetzner Cloud infrastructure
- User asks about server types, datacenters, locations, or images

## Installation

| Method | Command |
|--------|---------|
| Homebrew | `brew install hcloud` |
| Docker | `docker run --rm -e HCLOUD_TOKEN="..." hetznercloud/cli:latest <cmd>` |
| Go | `go install github.com/hetznercloud/cli/cmd/hcloud@latest` |
| Linux tarball | download from [GitHub releases](https://github.com/hetznercloud/cli/releases) |
| .deb / .rpm | download from releases (experimental) |
| WinGet | `winget install HetznerCloud.CLI` |
| Scoop | `scoop install hcloud` |

## Authentication

```bash
# Persistent context
hcloud context create <name>   # prompted for API token
hcloud context use <name>

# Stateless (overrides config — use for CI/CD)
export HCLOUD_TOKEN="<your-api-token>"
```

Create tokens at: https://console.hetzner.com → project → Security → API Tokens

## End-to-End Server Workflow

```bash
# 1. Upload SSH key
hcloud ssh-key create --name my-ssh-key --public-key-from-file ~/.ssh/hcloud.pub

# 2. (Optional) Set as default so --ssh-key can be omitted
hcloud config set default-ssh-keys my-ssh-key

# 3. Create server
hcloud server create --name my-server --type cpx22 --image ubuntu-24.04 --ssh-key my-ssh-key

# 4. Connect viaSSH
hcloud server ssh my-server -i ~/.ssh/hcloud

# 5. Clean up
hcloud server delete my-server
hcloud ssh-key delete my-ssh-key
```

Check available types: `hcloud server-type list`, images: `hcloud image list`, locations: `hcloud location list`.

## Shell Completions

```bash
hcloud completion bash       # Bash: source <(hcloud completion bash)
hcloud completion zsh        # Zsh: save to fpath
hcloud completion fish       # Fish: source
hcloud completion powershell # PowerShell: Out-String | Invoke-Expression
```

## Gotchas

- `HCLOUD_TOKEN` env var overrides config contexts — use for CI/CD, config for interactive
- `server create` without `--ssh-key` → no SSH access, must use web console
- Deleting a server is permanent — no recycle bin
- DNS: `hcloud zone` manages the zone, `hcloud zone rrset` manages individual records within a zone
- `.deb`/`.rpm` packages are experimental per upstream
- Tab completion is not automatic (except via .deb/.rpm) — must be configured per shell

## References

Load these on demand:

- [Resource commands](references/COMMANDS.md) — all resource commands and subcommands
- [Output options](references/OUTPUT.md) — JSON, YAML, Go templates, table column filtering
- [Configuration & CLI](references/CONFIG.md) — config file, contexts, env vars, global flags
