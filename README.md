dotnet-pre-commit-mirror-maker
==============================

Scripts for creating [prek](https://github.com/j178/prek) mirror repositories for dotnet tools
that do not ship their own `.pre-commit-hooks.yaml`.

Forked from [pre-commit-mirror-maker](https://github.com/pre-commit/pre-commit-mirror-maker)
by [Anthony Sottile](https://github.com/asottile), stripped down to dotnet
tool support only.


### How it works

For every stable version of a NuGet tool package the mirror maker creates a
tagged commit containing:

| File | Purpose |
|---|---|
| `.pre-commit-hooks.yaml` | Hook manifest consumed by pre-commit / prek |
| `.version` | Tracks the last mirrored version |
| `LICENSE` | MIT licence carried from this project |

The hook uses `additional_dependencies` so that pre-commit / prek can install
the tool with `dotnet tool install` — no `.config/dotnet-tools.json` or
placeholder project is needed in the mirror.


### Installation

```console
$ pip install dotnet-pre-commit-mirror-maker
```


### Usage

```console
$ dotnet-pre-commit-mirror --help
```

Example — mirror [csharpier](https://csharpier.com):

```console
$ git init mirrors-csharpier
Initialized empty Git repository in /tmp/mirrors-csharpier/.git/

$ dotnet-pre-commit-mirror mirrors-csharpier \
    --language dotnet \
    --package-name csharpier \
    --entry 'csharpier format' \
    --files-regex '\.cs$'
[main (root-commit) 5535fbb] Mirror: 0.8.1
 3 files changed, 30 insertions(+)
 create mode 100644 .pre-commit-hooks.yaml
 create mode 100644 .version
 create mode 100644 LICENSE
...
[main 56dba3a] Mirror: 1.2.6
 2 files changed, 2 insertions(+), 2 deletions(-)

$ ls mirrors-csharpier/
.git/  .pre-commit-hooks.yaml  .version  LICENSE
```

Then point your `.pre-commit-config.yaml` (or `prek.toml`) at the mirror:

```yaml
repos:
  - repo: https://github.com/your-org/mirrors-csharpier
    rev: v1.2.6
    hooks:
      - id: csharpier
```


### Credits

The original multi-language `pre-commit-mirror-maker` was created by
[Anthony Sottile](https://github.com/asottile) and is available at
<https://github.com/pre-commit/pre-commit-mirror-maker>.
This fork retains only dotnet tool support.


### License

MIT — see [LICENSE](LICENSE).
