# Configuration

Config file: `~/.config/hcloud/cli.toml` (override via `$HCLOUD_CONFIG` or `--config`)

**Priority** (higher wins): CLI flags > env vars > config file > defaults

## Config Commands

```bash
hcloud config list
hcloud config set <key> <value>
hcloud config get <key>
hcloud config unset <key>
```

## Context Management

```bash
hcloud context create <name>
hcloud context activate <name>
hcloud context use <name>
hcloud context list
hcloud context active
hcloud context rename <old> <new>
hcloud context delete <name>
```

## Global CLI Flags

| Flag | Description |
|------|-------------|
| `--config string` | Config file path (default `~/.config/hcloud/cli.toml`) |
| `--context string` | Active context name |
| `--debug` | Enable debug output |
| `--debug-file string` | Write debug output to file |
| `--endpoint string` | API endpoint (default `https://api.hetzner.cloud/v1`) |
| `--hetzner-endpoint string` | Hetzner API endpoint (default `https://api.hetzner.com/v1`) |
| `-h, --help` | Help |
| `--poll-interval duration` | Action poll interval (default `500ms`) |
| `--quiet` | Error messages only |
| `--no-experimental-warnings` | Suppress experimental warnings |
