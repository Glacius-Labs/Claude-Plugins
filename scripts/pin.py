"""Pin a plugin of the catalog to a release tag.

    python3 scripts/pin.py PLUGIN TAG

It writes the tag as `ref` and the commit the tag points at as `sha` into the entry
of PLUGIN in .claude-plugin/marketplace.json. Run scripts/check_marketplace.py
afterwards; it also runs in CI."""

import json
import sys

import check_marketplace as check

PATH = ".claude-plugin/marketplace.json"


def main(plugin_name, tag):
    with open(PATH, encoding="utf-8") as f:
        market = json.load(f)
    for plugin in market["plugins"]:
        if plugin.get("name") != plugin_name:
            continue
        source = plugin["source"]
        found = check.URL.match(source.get("url", ""))
        if not found:
            check.fail("%s: url must be the https address of a GitHub repository" % plugin_name)
        if not check.TAG.match(tag):
            check.fail("%r is no release tag such as v1.2.3" % tag)
        commit = check.tag_commit(found.group(1), tag)
        if commit is None:
            check.fail("the tag %s does not exist in %s" % (tag, found.group(1)))
        source["ref"], source["sha"] = tag, commit
        with open(PATH, "w", encoding="utf-8", newline="\n") as f:
            json.dump(market, f, indent=2, ensure_ascii=False)
            f.write("\n")
        print("%s pinned to %s (%s)" % (plugin_name, tag, commit))
        return
    check.fail("the catalog has no plugin %s" % plugin_name)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    main(sys.argv[1], sys.argv[2])
