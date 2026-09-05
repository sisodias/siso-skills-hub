#!/usr/bin/env python3
import os
import importlib.util
import subprocess
import sys
import tempfile
from pathlib import Path

SCRIPT = Path(__file__).parents[1] / "registry/skills/global/writeback/scripts/writeback.py"
ENTRY = "2026-09-05T12:00:00+00:00 · P5_OWNER · [p5:v1:opaque keep] what · notes/hand-off.md"
SPEC = importlib.util.spec_from_file_location("writeback", SCRIPT)
WRITEBACK = importlib.util.module_from_spec(SPEC); SPEC.loader.exec_module(WRITEBACK)


def call(repo, root, entry=ENTRY):
    return subprocess.run([sys.executable, str(SCRIPT), "--repo", str(repo), "--a0-root", str(root), "--entry", entry], text=True, capture_output=True)


def main():
    with tempfile.TemporaryDirectory() as td:
        base = Path(td); repo = base / "repo"; root = base / "a0"; repo.mkdir(); root.mkdir()
        (repo / ".agents").mkdir(); (root / "ledger").mkdir()
        old_local = b"old local\n"; old_ledger = b"# Owners\n- old ledger\n"
        (repo / ".agents/owners.log").write_bytes(old_local); (root / "ledger/OWNERS.md").write_bytes(old_ledger)
        r = call(repo, root); assert r.returncode == 0, r.stderr
        assert (repo / ".agents/owners.log").read_bytes() == old_local + (ENTRY + "\n").encode()
        assert (root / "ledger/OWNERS.md").read_bytes() == old_ledger + (ENTRY + "\n").encode()
        assert call(repo, root).returncode == 0
        assert (repo / ".agents/owners.log").read_bytes().count(ENTRY.encode()) == 1
        (root / "ledger/OWNERS.md").write_bytes(old_ledger + b"- " + (ENTRY + "\n").encode())
        assert call(repo, root).returncode == 0
        # A mirror failure retains the local durable line; fixing the mirror makes retry safe.
        mirror = root / "ledger/OWNERS.md"
        mirror.unlink(); mirror.symlink_to(base / "missing-ledger")
        failed_entry = ENTRY.replace("opaque keep", "mirror retry")
        assert call(repo, root, failed_entry).returncode != 0
        assert failed_entry.encode() in (repo / ".agents/owners.log").read_bytes()
        mirror.unlink(); mirror.write_bytes(b"")
        assert call(repo, root, failed_entry).returncode == 0
        assert (mirror.read_bytes()).count(failed_entry.encode()) == 1
        (root / "ledger/OWNERS.md").write_bytes(old_ledger); (root / "ledger/OWNERS.md.p5.lock").write_text("999\n")
        assert call(repo, root).returncode != 0; (root / "ledger/OWNERS.md.p5.lock").unlink()
        (repo / ".agents/owners.log").write_bytes(b"partial"); assert call(repo, root).returncode != 0
        (repo / ".agents/owners.log").unlink(); (repo / ".agents").rmdir(); (repo / ".agents").symlink_to(base / "elsewhere", target_is_directory=True)
        assert call(repo, root).returncode != 0
        (repo / ".agents").unlink(); (repo / ".agents").mkdir()
        entries = [ENTRY.replace("opaque keep", f"concurrent-{n}") for n in (1, 2)]
        procs = [subprocess.Popen([sys.executable, str(SCRIPT), "--repo", str(repo), "--a0-root", str(root), "--entry", e], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True) for e in entries]
        results = [p.wait() for p in procs]
        for e, code in zip(entries, results):
            if code: assert call(repo, root, e).returncode == 0
        local = (repo / ".agents/owners.log").read_bytes(); mirrored = (root / "ledger/OWNERS.md").read_bytes()
        assert all(local.count(e.encode()) == mirrored.count(e.encode()) == 1 for e in entries)
        # Validation happens against real targets and does not mutate either file.
        before_local = local; before_mirror = mirrored
        for bad in ("bad", "2026-09-05T12:00:00 · P5_OWNER · x · y", "2026-09-05T12:00:00+00:00 · p5 · x · y", "2026-09-05T12:00:00+00:00 · P5_OWNER · x\ny · y", ENTRY + "\u2028", ENTRY.replace("what", "x\u2029y"), "2026-09-05T12:00:00Z · P5_OWNER ·   · path.md"):
            result = call(repo, root, bad); assert result.returncode != 0 and result.stderr.startswith("writeback failed:")
            assert (repo / ".agents/owners.log").read_bytes() == before_local
            assert (root / "ledger/OWNERS.md").read_bytes() == before_mirror
        # Additive cap rejects a line that would exceed the bounded log.
        local_path = repo / ".agents/owners.log"
        room = 4 * 1024 * 1024 - len((ENTRY + "\n").encode())
        local_path.write_bytes(b"x\n" * ((room + 1) // 2))
        snapshot = local_path.read_bytes(); assert call(repo, root).returncode != 0; assert local_path.read_bytes() == snapshot
        local_path.write_bytes(before_local)
        # FIFO and directory targets are rejected without opening a blocking read.
        local_path.unlink(); local_path.mkdir(); assert call(repo, root).returncode != 0; local_path.rmdir()
        os.mkfifo(local_path); assert call(repo, root).returncode != 0; local_path.unlink(); local_path.write_bytes(before_local)
        # A short low-level write fails explicitly while retaining the partial bytes.
        short_path = base / "short.log"; short_path.write_bytes(b"")
        original_write = WRITEBACK.os.write
        WRITEBACK.os.write = lambda fd, data: original_write(fd, data[:-1])
        try:
            try: WRITEBACK._append(short_path, b"abcdef")
            except WRITEBACK.WritebackError as exc: assert "short append" in str(exc)
            else: assert False, "short append was accepted"
        finally: WRITEBACK.os.write = original_write
        assert short_path.read_bytes() == b"abcde"
    print("writeback tests: behavioral suite passed")


if __name__ == "__main__": main()
