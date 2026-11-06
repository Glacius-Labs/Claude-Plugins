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

If the clone over SSH fails because you have no GitHub key, add the marketplace by its https address: `claude plugin marketplace add https://github.com/Glacius-Labs/Claude-Plugins.git`.

## How this repository works

`.claude-plugin/marketplace.json` is the whole marketplace. Each entry names a plugin and pins the source it comes from to a release: the tag (`ref`) and the commit it points at (`sha`). So a plugin changes for users only when its entry changes here, and a tag that is moved later changes nothing. A plugin repository is never installed from its `main`.

To publish a new release of a plugin, wait until the release is published and its own checks are green, then:

```bash
python3 scripts/pin.py markitect v0.17.0
python3 scripts/check_marketplace.py
```

Commit the change and push. `check_marketplace.py` also runs in CI (`.github/workflows/validate.yaml`). It refuses an entry whose tag does not exist or is at another commit than the pinned one, whose release is not published, or whose plugin at that commit has another name or a version other than the tag.

## License

Apache License 2.0, see [LICENSE](LICENSE).
