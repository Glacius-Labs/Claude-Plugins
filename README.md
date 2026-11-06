# Claude-Plugins

The plugin marketplace of Glacius Labs for [Claude Code](https://claude.com/claude-code). The marketplace is called `glacius-labs`; a plugin installs as `<plugin>@glacius-labs`.

```bash
claude plugin marketplace add Glacius-Labs/Claude-Plugins
claude plugin install markitect@glacius-labs
```

## Plugins

| Plugin | What it does | Source |
| --- | --- | --- |
| `markitect` | Brings the `markitect` command into Claude Code's shell and tells every session what [Markitect](https://github.com/Glacius-Labs/Markitect) is. It downloads the binary of its own release the first time. | [`plugin/`](https://github.com/Glacius-Labs/Markitect/tree/main/plugin) in Markitect |

## Updating

```bash
claude plugin marketplace update glacius-labs
claude plugin update markitect@glacius-labs
```

## How this repository works

`.claude-plugin/marketplace.json` is the whole marketplace. Each entry names a plugin and pins the source it comes from to a release tag, so a plugin changes for users only when its entry changes here. A plugin repository is never installed from its `main`.

To publish a new release of a plugin, change `ref` of its entry to the new tag and push. The check in `.github/workflows/validate.yaml` refuses an entry whose tag does not exist.

## License

Apache License 2.0, see [LICENSE](LICENSE).
