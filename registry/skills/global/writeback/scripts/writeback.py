#!/usr/bin/env python3
"""Append one owner line locally, then mirror the exact bytes to the ledger."""
from __future__ import annotations

import argparse
import os
import re
import stat
import sys
from datetime import datetime
from pathlib import Path

MAX_BYTES = 16 * 1024
MAX_LOG_BYTES = 4 * 1024 * 1024
SEP = " · "
OWNER = re.compile(r"[A-Z][A-Z0-9_-]{0,31}\Z")


class WritebackError(Exception):
    pass


def _safe_child(root: Path, *parts: str) -> Path:
    root = root.resolve()
    target = root.joinpath(*parts)
    try:
        target.relative_to(root)
    except ValueError as exc:
        raise WritebackError("target escapes requested root") from exc
    return target


def _root_dir(path: Path) -> Path:
    if path.is_symlink() or not path.is_dir():
        raise WritebackError(f"requested root is not a real directory: {path}")
    return path.resolve()


def _ensure_dir(path: Path) -> None:
    if path.exists() or path.is_symlink():
        if path.is_symlink() or not path.is_dir():
            raise WritebackError(f"refusing unsafe directory: {path}")
        return
    path.mkdir()


def _check_file(path: Path) -> None:
    if path.is_symlink():
        raise WritebackError(f"refusing symlink: {path}")
    if path.exists() and not path.is_file():
        raise WritebackError(f"refusing non-regular file: {path}")


def _read(path: Path) -> bytes:
    try:
        fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
    except FileNotFoundError:
        return b""
    try:
        st = os.fstat(fd)
        if not stat.S_ISREG(st.st_mode):
            raise WritebackError(f"refusing non-regular file: {path}")
        if st.st_size > MAX_LOG_BYTES:
            raise WritebackError(f"ledger exceeds {MAX_LOG_BYTES} bytes: {path}")
        chunks = []
        total = 0
        while True:
            chunk = os.read(fd, min(65536, MAX_LOG_BYTES + 1 - total))
            if not chunk:
                break
            chunks.append(chunk); total += len(chunk)
            if total > MAX_LOG_BYTES:
                raise WritebackError(f"ledger exceeds {MAX_LOG_BYTES} bytes: {path}")
        data = b"".join(chunks)
        if data and not data.endswith(b"\n"):
            raise WritebackError(f"refusing partial log tail: {path}")
        return data
    finally:
        os.close(fd)


def _contains(data: bytes, entry: bytes) -> bool:
    entry = entry.rstrip(b"\n")
    return any(line == entry or line == b"- " + entry for line in data.splitlines())


def _append(path: Path, data: bytes) -> None:
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_APPEND | os.O_NOFOLLOW | os.O_NONBLOCK, 0o600)
    try:
        st = os.fstat(fd)
        if not stat.S_ISREG(st.st_mode):
            raise WritebackError(f"refusing non-regular file: {path}")
        written = os.write(fd, data)
        if written != len(data):
            raise WritebackError(f"short append ({written}/{len(data)} bytes): {path}")
        os.fsync(fd)
    finally:
        os.close(fd)
    try:
        dirfd = os.open(path.parent, os.O_RDONLY | os.O_DIRECTORY)
        try:
            os.fsync(dirfd)
        finally:
            os.close(dirfd)
    except OSError as exc:
        raise WritebackError(f"unable to fsync parent directory: {path.parent}") from exc


def validate_entry(entry: str) -> bytes:
    raw = entry.encode("utf-8")
    if not raw or len(raw) > MAX_BYTES or entry.splitlines() != [entry]:
        raise WritebackError("entry must be one nonempty UTF-8 line no longer than 16KiB")
    if any(ord(ch) < 32 or ord(ch) == 127 for ch in entry):
        raise WritebackError("entry contains control characters")
    fields = entry.split(SEP)
    if len(fields) != 4 or any(not field.strip() for field in fields):
        raise WritebackError("entry must contain exactly 4 nonempty fields separated by ' · '")
    try:
        stamp = datetime.fromisoformat(fields[0].replace("Z", "+00:00"))
    except ValueError as exc:
        raise WritebackError("timestamp must be ISO8601") from exc
    if stamp.tzinfo is None or stamp.utcoffset() is None:
        raise WritebackError("timestamp must include a timezone")
    if not OWNER.fullmatch(fields[1]):
        raise WritebackError("owner must be uppercase letters/digits/_/- (max 32 chars)")
    return raw + b"\n"


def run(repo: Path, a0_root: Path, entry: str) -> int:
    line = validate_entry(entry)
    repo = _root_dir(repo)
    a0_root = _root_dir(a0_root)
    local_dir = _safe_child(repo, ".agents")
    ledger_dir = _safe_child(a0_root, "ledger")
    _ensure_dir(local_dir)
    _ensure_dir(ledger_dir)
    local = _safe_child(repo, ".agents", "owners.log")
    ledger = _safe_child(a0_root, "ledger", "OWNERS.md")
    lock = _safe_child(a0_root, "ledger", "OWNERS.md.p5.lock")
    _check_file(lock)
    try:
        fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError as exc:
        raise WritebackError("writeback lock is held") from exc
    lock_identity = None
    try:
        lock_identity = os.fstat(fd)
        os.write(fd, f"{os.getpid()}\n".encode())
        os.fsync(fd)
        local_data = _read(local)
        if not _contains(local_data, line):
            if len(local_data) + len(line) > MAX_LOG_BYTES:
                raise WritebackError(f"log would exceed {MAX_LOG_BYTES} bytes: {local}")
            _append(local, line)
        try:
            ledger_data = _read(ledger)
            if not _contains(ledger_data, line):
                if len(ledger_data) + len(line) > MAX_LOG_BYTES:
                    raise WritebackError(f"ledger would exceed {MAX_LOG_BYTES} bytes: {ledger}")
                _append(ledger, line)
        except Exception as exc:
            print(f"local durable / mirror pending: {exc}", file=sys.stderr)
            return 2
        print("writeback complete")
        return 0
    finally:
        os.close(fd)
        try:
            current = lock.lstat()
            if lock_identity is not None and (current.st_dev, current.st_ino) == (lock_identity.st_dev, lock_identity.st_ino):
                lock.unlink()
        except OSError:
            pass


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", required=True, type=Path)
    parser.add_argument("--a0-root", required=True, type=Path)
    parser.add_argument("--entry", required=True)
    args = parser.parse_args()
    try:
        return run(args.repo, args.a0_root, args.entry)
    except (WritebackError, OSError) as exc:
        print(f"writeback failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
