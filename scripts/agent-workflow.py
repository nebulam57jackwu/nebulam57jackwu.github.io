#!/usr/bin/env python3
"""Cooperative ownership and verification receipts; Linux/macOS."""
import argparse
import datetime
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess


def git(*args):
    return subprocess.check_output(["git", *args])


def main():
    p = argparse.ArgumentParser()
    p.add_argument("action", choices=["status", "claim", "release", "recover", "verify", "check"])
    p.add_argument("--owner")
    p.add_argument("--previous-owner")
    args = p.parse_args()
    root = Path(git("rev-parse", "--show-toplevel").decode().strip())
    os.chdir(root)
    manifest = json.loads(Path(".dual-agent-kit.json").read_text())
    handoff = (root / manifest["handoff"]).resolve()
    if not handoff.is_relative_to(root):
        raise SystemExit("Handoff escapes repository")
    state = Path(git("rev-parse", "--absolute-git-dir").decode().strip()) / "agent-workflow"
    state.mkdir(exist_ok=True)
    owner_file, receipt = state / "owner.json", state / "verification.json"

    def fingerprint():
        digest = hashlib.sha256()
        digest.update(subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True).stdout)
        digest.update(git("diff", "--cached", "--binary", "--", ".", ":(exclude)" + manifest["handoff"]))
        paths = git("ls-files", "-z", "--cached", "--others", "--exclude-standard").split(b"\0")
        for raw in sorted(set(paths)):
            if not raw:
                continue
            path = root / os.fsdecode(raw)
            if path.resolve() == handoff:
                continue
            digest.update(raw + b"\0")
            if path.is_symlink():
                digest.update(os.readlink(path).encode())
            elif path.is_file():
                digest.update(str(path.stat().st_mode).encode())
                digest.update(path.read_bytes())
            else:
                digest.update(b"MISSING")
        return digest.hexdigest()

    with (state / "mutex").open("a") as mutex:
        fcntl.flock(mutex, fcntl.LOCK_EX)
        owner = json.loads(owner_file.read_text())["owner"] if owner_file.exists() else None
        text = handoff.read_text()
        fields = re.findall(r"^Writer: (.+)$", text, re.M)
        if len(fields) != 1:
            raise SystemExit("Handoff needs exactly one 'Writer: ...' field")
        writer = fields[0]
        if args.action in ("claim", "release", "recover"):
            if not args.owner or not re.fullmatch(r"[A-Za-z0-9_.-]+", args.owner):
                raise SystemExit("Use --owner with a unique session identifier (letters/digits/._-)")
            if args.action == "claim":
                if owner is not None or writer != "RELEASED":
                    raise SystemExit(f"Already owned: {owner or writer}")
                owner_file.write_text(json.dumps({"owner": args.owner}))
                replacement = f"{args.owner} (ACTIVE)"
            elif args.action == "release":
                if owner != args.owner:
                    raise SystemExit("Only the recorded owner can release")
                replacement = "RELEASED"
            else:
                if not owner or args.previous_owner != owner:
                    raise SystemExit("Recovery requires exact --previous-owner; first confirm that session stopped")
                replacement = "RELEASED"
            handoff.write_text(re.sub(r"^Writer: .+$", "Writer: " + replacement, text, flags=re.M))
            if args.action != "claim":
                owner_file.unlink()
            print(replacement)
            return
        if args.action == "verify":
            before = fingerprint()
            result = subprocess.run(["bash", "scripts/verify.sh"])
            after = fingerprint()
            receipt.write_text(json.dumps({"fingerprint": after, "passed": result.returncode == 0 and before == after,
                                           "checked_at": datetime.datetime.now().astimezone().isoformat()}))
            if result.returncode or before != after:
                raise SystemExit(result.returncode or "Files changed during verification; rerun")
            return
        evidence = json.loads(receipt.read_text()) if receipt.exists() else {}
        fresh = evidence.get("passed") and evidence.get("fingerprint") == fingerprint()
        print(json.dumps({"owner": owner, "writer": writer, "verification_current": bool(fresh),
                          "checked_at": evidence.get("checked_at"), "upgrade_status": manifest.get("upgrade_status", "unknown")}, indent=2))
        subprocess.run(["git", "status", "--short"], check=True)
        if args.action == "check" and (owner or writer != "RELEASED" or not fresh):
            raise SystemExit("Not ready: release ownership and obtain a current passing verification receipt")


if __name__ == "__main__":
    main()
