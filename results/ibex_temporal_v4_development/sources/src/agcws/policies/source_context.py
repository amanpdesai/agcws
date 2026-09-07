"""Allowlisted source excerpts and receipts, separate from candidate execution."""

import hashlib
import json
from pathlib import Path


def _inside(root, name):
    if Path(name).is_absolute() or ".." in Path(name).parts:
        raise ValueError("relative allowlisted paths required")
    path = root / name
    if not path.resolve().is_relative_to(root.resolve()):
        raise ValueError("source escapes bundle root")
    return path


def build_bundle(root, destination, names):
    """Copy explicit files only; never discover files from the repository."""
    if len(set(names)) != len(names) or not names:
        raise ValueError("nonempty unique allowlist required")
    records = {}
    contents = {}
    for name in names:
        source = _inside(root, name)
        data = source.read_bytes()
        data.decode("utf-8")
        contents[name] = data
        records[name] = {"sha256": hashlib.sha256(data).hexdigest(), "bytes": len(data)}
    destination.mkdir(parents=True, exist_ok=False)
    for name, data in contents.items():
        target = _inside(destination, name)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
        target.chmod(0o444)
    manifest = destination / "manifest.json"
    manifest.write_text(json.dumps({"files": records}, indent=2) + "\n")
    manifest.chmod(0o444)
    return records


class SourceReader:
    """A bounded retrieval interface; a receipt proves access, not understanding."""

    def __init__(self, root, manifest_sha256, max_chars=40000):
        data = (root / "manifest.json").read_bytes()
        if hashlib.sha256(data).hexdigest() != manifest_sha256:
            raise ValueError("source manifest hash mismatch")
        if max_chars <= 0:
            raise ValueError("positive context budget required")
        self.root, self.remaining = root, max_chars
        self.files = json.loads(data)["files"]
        self.receipts = []

    def read(self, name, start, stop):
        if name not in self.files:
            raise ValueError("source is not allowlisted")
        if type(start) is not int or type(stop) is not int or not 1 <= start <= stop:
            raise ValueError("positive inclusive line range required")
        data = _inside(self.root, name).read_bytes()
        digest = hashlib.sha256(data).hexdigest()
        if digest != self.files[name]["sha256"]:
            raise ValueError("source file hash mismatch")
        lines = data.decode("utf-8").splitlines()
        if stop > len(lines):
            raise ValueError("line range exceeds file")
        text = "\n".join(f"{i}: {lines[i - 1]}" for i in range(start, stop + 1))
        if len(text) > self.remaining:
            raise ValueError("source context budget exhausted")
        self.remaining -= len(text)
        receipt = {
            "file": name,
            "sha256": digest,
            "start": start,
            "stop": stop,
            "characters": len(text),
        }
        self.receipts.append(receipt)
        return {"text": text, "receipt": receipt}
