# Output Options

All `describe`, `list`, and `create` commands support `--output`.

## JSON

```bash
hcloud location describe fsn1 --output json
hcloud location list --output json | jq '[.[] | select(.network_zone == "eu-central") | .name]'
```

## YAML

```bash
hcloud location describe fsn1 --output yaml
hcloud location list --output yaml | yq '.[] | [{"id": .id, "name": .name}]'
```

## Go Template (describe only)

```bash
hcloud server describe my-server --output format='{{.ServerType.Cores}}'
```

Data structures follow the [hcloud-go schema](https://pkg.go.dev/github.com/hetznercloud/hcloud-go/v2/hcloud/schema).

## Table Options (list only)

```bash
hcloud location list --output noheader
hcloud location list --output columns=id,name,network_zone
hcloud location list --output noheader --output columns=id,name
```

Available columns are shown in `--help`. Combine both: `--output noheader --output columns=id,name`.
