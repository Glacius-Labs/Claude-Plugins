"""Check .claude-plugin/marketplace.json: the shape Claude Code needs, and that every
pinned release tag exists in the repository it names."""

import json
import re
import subprocess
import sys

KEBAB = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
TAG = re.compile(r"^v[0-9]+\.[0-9]+\.[0-9]+(-[0-9A-Za-z.-]+)?$")


def fail(message):
    print("marketplace: " + message, file=sys.stderr)
    sys.exit(1)


def main(path):
    with open(path, encoding="utf-8") as f:
        market = json.load(f)
    if not KEBAB.match(market.get("name", "")):
        fail("the marketplace needs a kebab-case name")
    if not market.get("owner", {}).get("name"):
        fail("the marketplace needs an owner name")
    plugins = market.get("plugins")
    if not plugins:
        fail("the marketplace lists no plugin")
    seen = set()
    for plugin in plugins:
        name = plugin.get("name", "")
        if not KEBAB.match(name):
            fail("a plugin needs a kebab-case name: %r" % name)
        if name in seen:
            fail("the plugin %s is listed twice" % name)
        seen.add(name)
        source = plugin.get("source")
        if not isinstance(source, dict) or source.get("source") != "git-subdir":
            fail("%s: the source must be a git-subdir pinned to a release tag" % name)
        url, ref = source.get("url", ""), source.get("ref", "")
        # The full https address: the owner/repo shorthand makes Claude Code try SSH
        # first, which fails for anyone without a GitHub key.
        found = re.match(r"^https://github\.com/([A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+?)(?:\.git)?$", url)
        if not found:
            fail("%s: url must be the https address of a GitHub repository: %r" % (name, url))
        repo = found.group(1)
        if not TAG.match(ref):
            fail("%s: ref must be a release tag such as v1.2.3: %r" % (name, ref))
        if not source.get("path"):
            fail("%s: the source needs the path of the plugin in the repository" % name)
        out = subprocess.run(
            ["git", "ls-remote", "--tags", "https://github.com/%s.git" % repo, "refs/tags/" + ref],
            capture_output=True, text=True,
        )
        if out.returncode != 0 or not out.stdout.strip():
            fail("%s: the tag %s does not exist in %s" % (name, ref, repo))
        print("ok: %s at %s of %s" % (name, ref, repo))


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else ".claude-plugin/marketplace.json")
