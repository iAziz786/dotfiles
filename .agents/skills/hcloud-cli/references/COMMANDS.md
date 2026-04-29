# hcloud Resource Commands

All resources follow the same pattern: `create`, `list`, `describe`, `update`, `delete`, `add-label`, `remove-label`. Resource-specific subcommands are listed below.

| Resource | Root Command | Key Subcommands |
|----------|-------------|-----------------|
| Server | `hcloud server` | `create`, `list`, `describe`, `delete`, `update`, `ssh`, `reboot`, `reset`, `shutdown`, `poweroff`, `poweron`, `reset-password`, `enable-rescue`, `disable-rescue`, `attach-iso`, `detach-iso`, `enable-backup`, `disable-backup`, `enable-protection`, `disable-protection`, `change-type`, `rebuild`, `create-image`, `request-console`, `metrics`, `ip`, `attach-to-network`, `detach-from-network`, `change-alias-ips`, `add-to-placement-group`, `remove-from-placement-group` |
| Firewall | `hcloud firewall` | `create`, `list`, `describe`, `delete`, `update`, `add-rule`, `remove-rule`, `replace-rules`, `apply-to-resource`, `remove-from-resource` |
| Network | `hcloud network` | `create`, `list`, `describe`, `delete`, `update`, `add-subnet`, `remove-subnet`, `add-route`, `remove-route`, `change-ip-range`, `expose-routes-to-vswitch` |
| Volume | `hcloud volume` | `create`, `list`, `describe`, `delete`, `update`, `attach`, `detach`, `resize` |
| SSH Key | `hcloud ssh-key` | `create`, `list`, `describe`, `delete`, `update` |
| Floating IP | `hcloud floating-ip` | `create`, `list`, `describe`, `delete`, `update`, `assign`, `unassign`, `set-rdns` |
| Primary IP | `hcloud primary-ip` | `create`, `list`, `describe`, `delete`, `update`, `assign`, `unassign`, `set-rdns` |
| Placement Group | `hcloud placement-group` | `create`, `list`, `describe`, `delete`, `update` |
| Load Balancer | `hcloud load-balancer` | `create`, `list`, `describe`, `delete`, `update`, `add-service`, `update-service`, `delete-service`, `add-target`, `remove-target`, `change-type`, `change-algorithm`, `metrics`, `attach-to-network`, `detach-from-network`, `enable-public-interface`, `disable-public-interface`, `set-rdns` |
| Certificate | `hcloud certificate` | `create`, `list`, `describe`, `delete`, `update`, `retry` |
| Image | `hcloud image` | `list`, `describe`, `delete`, `update` |
| ISO | `hcloud iso` | `list`, `describe` |
| Storage Box | `hcloud storage-box` | `create`, `list`, `describe`, `delete`, `update`, `change-type`, `snapshot`, `subaccount`, `folders`, `reset-password` |
| DNS Zone | `hcloud zone` | `create`, `list`, `describe`, `delete`, `update`, `add-records`, `remove-records`, `set-records`, `export-zonefile`, `import-zonefile`, `change-ttl`, `change-primary-nameservers` |
| DNS RRset | `hcloud zone rrset` | `create`, `list`, `describe`, `delete`, `update`, `add-records`, `remove-records`, `set-records`, `change-ttl` |

## Read-only Resources

| Resource | Command | Subcommands |
|----------|---------|-------------|
| Datacenter | `hcloud datacenter` | `list`, `describe` |
| Location | `hcloud location` | `list`, `describe` |
| Server Type | `hcloud server-type` | `list`, `describe` |
| Load Balancer Type | `hcloud load-balancer-type` | `list`, `describe` |
| Storage Box Type | `hcloud storage-box-type` | `list`, `describe` |

## Management Commands

| Command | Purpose |
|---------|---------|
| `hcloud all list` | List all resources |
| `hcloud version` | Print version |
| `hcloud completion bash\|zsh\|fish\|powershell` | Output shell completion code |
