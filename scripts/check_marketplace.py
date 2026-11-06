"""Check .claude-plugin/marketplace.json: the shape Claude Code needs, and for every
entry that its pin is a published release whose plugin is the one the entry names.

A pin is a release tag (`ref`) and the commit it points at (`sha`). The sha makes the
pin immutable: a tag that is moved later no longer matches, and this check fails.
Use scripts/pin.py to write a pin."""

import json
import re
import subprocess
import sys
import urllib.error
import urllib.request

KEBAB = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
TAG = re.compile(r"^v[0-9]+\.[0-9]+\.[0-9]+(-[0-9A-Za-z.-]+)?$")
SHA = re.compile(r"^[0-9a-f]{40}$")
URL = re.compile(r"^https://github\.com/([A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+?)(?:\.git)?$")


def fail(message):
    print("marketplace: " + message, file=sys.stderr)
    sys.exit(1)


def tag_commit(repo, tag):
    """The commit a tag points at, or None. An annotated tag is a Git object of its
    own, and ls-remote lists the commit under the tag's name followed by ^{}."""
    out = subprocess.run(
        ["git", "ls-remote", "--tags", "https://github.com/%s.git" % repo, "refs/tags/" + tag, "refs/tags/" + tag + "^{}"],
        capture_output=True, text=True,
    )
    if out.returncode != 0:
        return None
    shas = {}
    for line in out.stdout.splitlines():
        sha, ref = line.split("\t")
        shas[ref] = sha
    return shas.get("refs/tags/" + tag + "^{}") or shas.get("refs/tags/" + tag)


def fetch(url, method="GET"):
    request = urllib.request.Request(url, method=method, headers={"User-Agent": "claude-plugins-check"})
    with urllib.request.urlopen(request, timeout=30) as response:
        return response.read()


def source_of(plugin):
    name = plugin.get("name", "")
    source = plugin.get("source")
    if not isinstance(source, dict) or source.get("source") != "git-subdir":
        fail("%s: the source must be a git-subdir pinned to a release tag" % name)
    # The full https address: the owner/repo shorthand makes Claude Code try SSH
    # first, which fails for anyone without a GitHub key.
    found = URL.match(source.get("url", ""))
    if not found:
        fail("%s: url must be the https address of a GitHub repository: %r" % (name, source.get("url")))
    if not source.get("path"):
        fail("%s: the source needs the path of the plugin in the repository" % name)
    if not TAG.match(source.get("ref", "")):
        fail("%s: ref must be a release tag such as v1.2.3: %r" % (name, source.get("ref")))
    if not SHA.match(source.get("sha", "")):
        fail("%s: sha must be the 40-character commit of the tag; scripts/pin.py writes it" % name)
    return found.group(1), source["path"], source["ref"], source["sha"]


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
        repo, subdir, ref, sha = source_of(plugin)

        commit = tag_commit(repo, ref)
        if commit is None:
            fail("%s: the tag %s does not exist in %s" % (name, ref, repo))
        if commit != sha:
            fail("%s: the tag %s is at %s but the entry pins %s" % (name, ref, commit, sha))

        try:
            fetch("https://github.com/%s/releases/tag/%s" % (repo, ref), "HEAD")
        except urllib.error.URLError as error:
            fail("%s: %s has no published release %s (%s)" % (name, repo, ref, error))

        manifest_url = "https://raw.githubusercontent.com/%s/%s/%s/.claude-plugin/plugin.json" % (repo, sha, subdir.strip("/"))
        try:
            manifest = json.loads(fetch(manifest_url))
        except (urllib.error.URLError, ValueError) as error:
            fail("%s: no plugin.json at %s in %s: %s" % (name, subdir, ref, error))
        if manifest.get("name") != name:
            fail("%s: the plugin at %s names itself %r" % (name, ref, manifest.get("name")))
        if manifest.get("version") != ref[1:]:
            fail("%s: the plugin at %s says version %r, not %s" % (name, ref, manifest.get("version"), ref[1:]))
        print("ok: %s %s (%s) of %s" % (name, ref, sha[:12], repo))


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else ".claude-plugin/marketplace.json")
